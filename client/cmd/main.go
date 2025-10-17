package main

import (
	"bytes"
	"client/pkg/filewatch"
	"client/pkg/helper"
	"encoding/json"
	"fmt"
	"net/http"
)

func main() {
	// TODO
	// # Attempt to load credentials
	// # send them to server.
	// load up directories
	// send directories + last touched time to server
	// then the rest

	var userDetails credentials

	helper.ReadFromJson("./cmd/login_credentials.json", &userDetails)

	err := sendLoginRequest(userDetails)
	if err != nil {
		fmt.Printf("Error when logging in: %v", err)
	}

	filewatch.InitWatcher()
}

type credentials struct {
	Username string `json:"username"`
	Password string `json:"password"`
}

func sendLoginRequest(userDetails credentials) error {

	data, err := json.Marshal(userDetails)

	if err != nil {
		return err
	}

	resp, err := http.Post("http://localhost:5000/login", "application/json", bytes.NewBuffer(data))

	if err != nil {
		return err
	}

	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		fmt.Printf("request status not ok. Code: %v", resp.StatusCode)
	}

	return nil
}
