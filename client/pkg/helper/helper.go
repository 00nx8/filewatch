package helper

import (
	"encoding/json"
	"fmt"
	"log"
	"os"
	"strings"
)

type Directory struct {
	Path           string
	SubDirectories []Directory
	Files          []string
}
type DirectoryInformation struct {
	Name  string `json:"name"`
	Path  string `json:"path"`
	Owner string `json:"owner"`
}

func IsError(err error) {
	if err != nil {
		log.Fatal(err)
	}
}

func CreateDirectory(dir string) {
	// TODO
	// When the servers up this will also have to request the files in said directory.
	err := os.MkdirAll(dir, 0755)
	IsError(err)
	fmt.Printf("Created directory at %v", dir)
}

func AskChoice(question string) bool {
	format_string := []string{question, "(Y/n)"}
	fmt.Printf("%s", strings.Join(format_string, " "))

	var userInput string
	_, err := fmt.Scanln(&userInput)

	IsError(err)
	return userInput == "Y"
}

func ReadFromJson[T any](path string, dest *T) error {
	data, err := os.ReadFile(path)
	if err != nil {
		return err
	}

	err = json.Unmarshal(data, *dest)
	if err != nil {
		return err
	}

	return nil
}
