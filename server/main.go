package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
)

type FileEventPayload struct {
	Event     string `json:"event"`
	Path      string `json:"path"`
	Timestamp string `json:"timestamp"`
}

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

func main() {
	http.HandleFunc("/api/events", handleFileEvent)
	fmt.Println("Listening on :8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
}
