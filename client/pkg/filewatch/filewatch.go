package filewatch

import (
	"bytes"
	"client/pkg/helper"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/fsnotify/fsnotify"
)

// TODO:
// Newly created directories are not being watched.

// initialise a watcher with directories and subdirectories of a directory and start it.
func InitWatcher() {
	directories := loadSavedDirectories()
	// after that, find their sub directories.

	watcher, err := fsnotify.NewWatcher()
	helper.IsError(err)
	defer watcher.Close()

	for _, directory := range directories {
		err := discoverSubDirectories(watcher, directory.Path)
		helper.IsError(err)
	}
	filewatch(watcher)

}

type FileEventPayload struct {
	Event     string `json:"event"`
	Path      string `json:"path"`
	Timestamp string `json:"timestamp"`
}

func sendEventToServer(eventType, filePath string) {
	payload := FileEventPayload{
		Event:     eventType,
		Path:      filePath,
		Timestamp: time.Now().Format(time.RFC3339),
	}

	data, err := json.Marshal(payload)
	if err != nil {
		fmt.Println("Failed to marshal event:", err)
		return
	}

	resp, err := http.Post("http://localhost:8080/api/events", "application/json", bytes.NewBuffer(data))
	if err != nil {
		fmt.Println("Failed to send event:", err)
		return
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		fmt.Printf("Server returned non-OK status: %d\n", resp.StatusCode)
	}
}

// Starts watcher monitor
func filewatch(watcher *fsnotify.Watcher) {
	// Monitor files in a given directory.
	// Send updates to client api.
	go func() {
		for {
			select {
			case event, ok := <-watcher.Events:
				if !ok {
					return
				}
				fmt.Println("event:", event)
				if event.Has(fsnotify.Write) {
					fmt.Println("modified file:", event.Name)
					sendEventToServer("modified", event.Name)
				}
				if event.Has(fsnotify.Create) {
					fmt.Println("created file or dir:", event.Name)
					sendEventToServer("created", event.Name)
				}
				if event.Has(fsnotify.Remove) {
					fmt.Println("deleted file:", event.Name)
					sendEventToServer("deleted", event.Name)
				}
			case err, ok := <-watcher.Errors:
				if !ok {
					return
				}
				if err != nil {
					fmt.Println(err)
				}
			}
		}
	}()

	<-make(chan struct{})
}

// reads the contents of the default json file and loads the saved directories into a []helper.DirectoryInformation
func loadSavedDirectories() []helper.DirectoryInformation {
	data, err := os.ReadFile("./pkg/filewatch/head_directories.json")

	helper.IsError(err)

	var dir []helper.DirectoryInformation
	err = json.Unmarshal(data, &dir)
	helper.IsError(err)

	return dir
}

// map out sub directories and files of a given directory.
func discoverSubDirectories(watcher *fsnotify.Watcher, dir string) error {
	// Open and check path status
	targetInfo, err := os.Stat(dir)

	if os.IsNotExist(err) {
		strs := []string{"Directory at ", dir, "Does not exist. Would you like to create it?"}
		res := helper.AskChoice(strings.Join(strs, "\n"))

		if !res {
			return err
		}

		helper.CreateDirectory(dir)
		return discoverSubDirectories(watcher, dir)
	}

	if !targetInfo.IsDir() {
		return fmt.Errorf("provide a directory: %v", dir)
	}

	entries, err := os.ReadDir(dir)
	helper.IsError(err)
	watcher.Add(dir)

	for _, entry := range entries {
		if !entry.IsDir() {
			continue
		}

		subDir := filepath.Join(dir, entry.Name())

		err = discoverSubDirectories(watcher, subDir)
		helper.IsError(err)
	}
	return nil
}
