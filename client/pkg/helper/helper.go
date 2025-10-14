package helper

import "log"

type Directory struct {
	Path           string
	SubDirectories []Directory
	Files          []string
}
type DirectoryInformation struct {
	Name  string `json:"name"`
	Path  string `json:"Pame"`
	Owner string `json:"owner"`
}

func IsError(err error) {
	if err != nil {
		log.Fatal(err)
	}
}
