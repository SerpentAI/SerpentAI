# AIsaac - Changelog

## V10

* Major departure from the previous versions!
* Everything reverted back to pure DQN
* Implemented Double-DQN (DDQN) for stability
* Implemented Prioritized Experience Replay (PER)
* Added record tracking for time alive and lowest boss HP
* Streaming API has been launched. You can ask for credentials on Twitch or Discord

## V9

* There was a version 9

## V8

* There was a version 8

## V7

* Now possible to pass a frame cap to the FrameGrabber (default: 30fps)
* The FrameGrabber will now process an additional image at 1/8 width and 1/8 height grayscale and make that available
* GameFrame class now accepts pre-built frame variants in the constructor
* Abstracted the replay memory to its own class
* ReplayMemory now uses a numpy array with circular buffer instead of a collections.deque
* Fixed an important DQN implementation bug where the terminal states were not handled at all
* Removed balanced mini-batches
* Removed cross-validation after AI runs
* Increased mini-batch size to 64
* Increased learning rate to 1e-4
* Starting Epsilon value is now 0.5
* Experimenting with disabling the GC during gameplay
* Added a new statistic: Average Actions per Second (APS)
* Overall went from 1 APS to 4 APS with update. AIsaac now has faster reaction speeds.

## V6

* Another(!!) [neural network structure](https://github.com/SerpentAI/Serpent/blob/master/lib/machine_learning/reinforcement_learning/dqn.py#L300-L322) (Inception layer and ELU activations)
* Rewards are now properly scaled between -1 and 1
* Build a WAMP Component to dispatch analytics events to a Crossbar router
* Added an instance variable in the base GameAgent class to collect the start time of an episode
* Displaying the episode start time in the terminal output
* New AI run sound!

## V5

* Brand new, revised [neural network structure](https://github.com/SerpentAI/Serpent/blob/master/lib/machine_learning/reinforcement_learning/dqn.py#L332) (Thanks @jhaluska on Twitch!)
* Added a live cross-validation step after an AI and now outputing cross-validation loss
* Use octal code to clear terminal instead of subprocess.call(["clear"]) (Thanks @dtusk on GitHub!)

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
