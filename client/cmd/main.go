package main

import "client/pkg/filewatch"

// on any watcher.Event,
// I need to figure out if that event is something that is worth doing.
// Maybe build a timeline, and sync changes with server once x amount of time has passed
// since last edit?
func main() {
	filewatch.InitWatcher()
}
