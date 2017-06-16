# AIsaac - Changelog

## 0.4.0

* Switched optimizer clipping from clipnorm=1 to clipvalue=1
* Added a way to generate balanced mini-batches. It attempts to use 1 observation per combination of the action space
* Balanced mini-batches are used until we reach final Epsilon and then random ones are used
* Created a new reward function: -(1 / 5) for damage taken, (9 / 654) for damage dealt
* Created an analytics client for general use in the framework
* Tagged analytics events in the BOSS_TRAIN mode

## 0.3.0

* Added gradient clipping to optimizer
* Reduced the learning rate to 1-e5
* All image data is now float16 between 0-1. Sane loss values again.
* Epsilon now erodes faster. Half the steps erode to minimum Epsilon and the rest stay at minimum Epsilon
* Replaced the 4 color image Frame Stack with an 8 gray image Frame Stack
* Fixed a bug with the input controller that would not repress a pressed key at the end of a run that also appeared at the beginning of the next run.
* ETAs are now slightly less horrible.
* ADDED A GONG SOUND BEFORE PREDICTED RUNS! OMGOMGOMG
