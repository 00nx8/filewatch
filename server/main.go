package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
)

type userDetails struct {
	Username string `json:"username"`
	Password string `json:"password"`
}

type FileEventPayload struct {
	Event     string `json:"event"`
	Path      string `json:"path"`
	Timestamp string `json:"timestamp"`
}

var users []userDetails

func handleFileEvent(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
		return
	}
	var payload FileEventPayload
	err := json.NewDecoder(r.Body).Decode(&payload)
	if err != nil {
		http.Error(w, "Invalid JSON", http.StatusBadRequest)
		return
	}

	log.Printf("Received event: %s | Path: %s | Time: %s", payload.Event, payload.Path, payload.Timestamp)

	w.WriteHeader(http.StatusOK)
	fmt.Fprint(w, "Event received")
}

func handleCredentials(writer http.ResponseWriter, request *http.Request) {
	if request.Method != http.MethodPost {
		fmt.Printf("Invalid request Method: %v", request.Method)
		// sendResponse
		return
	}

	var credentials userDetails
	err := json.NewDecoder(request.Body).Decode(&credentials)
	if err != nil {
		fmt.Println(err)
	}
	for _, user := range users {
		if user.Username != credentials.Username {
			continue
		}

		if user.Password == credentials.Password {
			// send positive response with token.
		}
	}
	// check credentials.
	// TODO
	// setup a database : https://go.dev/doc/tutorial/database-access
}

func main() {
	loadCredentials()

	http.HandleFunc("/login", handleCredentials)
	http.HandleFunc("/api/events", handleFileEvent)
	fmt.Println("Listening on :8080")
	log.Fatal(http.ListenAndServe(":8080", nil))

}

func loadCredentials() []userDetails {
	err := ReadFromJson("./users.json", &users)

	if err != nil {
		fmt.Println(err)
		return nil
	}
	return users
}

func ReadFromJson[T any](path string, dest *T) error {
	data, err := os.ReadFile(path)
	if err != nil {
		return err
	}

	err = json.Unmarshal(data, dest)
	if err != nil {
		return err
	}

	return nil
}
