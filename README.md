![](https://s3.ca-central-1.amazonaws.com/serpent-ai-assets/SerpentFBCover.png)

# Serpent.AI - Game Agent Framework (Python)

[![](https://img.shields.io/badge/project-website-brightgreen.svg?colorB=1bcc6f&longCache=true)](http://serpent.ai)
[![](https://img.shields.io/badge/project-blog-brightgreen.svg?colorB=1bcc6f&longCache=true)](http://blog.serpent.ai)
[![](https://img.shields.io/badge/project-wiki-brightgreen.svg?colorB=1bcc6f&longCache=true)](https://github.com/SerpentAI/SerpentAI/wiki)    
[![](https://img.shields.io/badge/pypi-v2018.1.2-brightgreen.svg?colorB=007ec6&longCache=true)]()
[![](https://img.shields.io/badge/python-3.6-brightgreen.svg?colorB=007ec6&longCache=true)]()
[![](https://img.shields.io/badge/license-MIT-brightgreen.svg?colorB=007ec6&longCache=true)]()  
[![](https://img.shields.io/badge/twitter-@Serpent__AI-brightgreen.svg?colorB=1da1f2&longCache=true)](https://twitter.com/Serpent_AI)

### Plugin Showcases - Martyn:

[Bullet Heaven 2 Game Plugin](https://github.com/Martyn0324/SerpentBullet_HeavenGamePlugin) ---- [Bullet Heaven 2 Game Agent](https://github.com/Martyn0324/SerpentNimbleAngelGameAgentPlugin)


## Update: Shaking off the dust (October 2021) - Martyn

Unfortunately, Nicholas Brochu(the founder of SerpentAI) seems to have definitely ceased developing SerpentAI. However, since this project is, probably, the only one that is really interesting in terms of Reinforcement Learning thanks to the possibility of using AIs to play **ANY** game, I decided to make a fork and try to modify a few things in order to make SerpentAI functional.

I've began to study programming in order to be able to develop AIs capable of playing games, initially, and then able to do anything that could prove useful(like predicting stock market).
However, as I've studied and searched about Reinforcement Learning, I discovered that this area is really underrated or, at least, doesn't arouse that much interest between programmers in general. Why's that? Well, because every algorithm people develop is to be played in OpenAI's Gym, which only allows for playing games from Atari, SNES, etc. The only option that would go a little bit further than that is OpenAI's Universe, which only allows for playing browser games.
The result is that we can only apply Reinforcement Learning to some simple, limited games, with few options to improvement. And while we are stuck in this situation, [OpenAI develops algorithms able to play complex games such as Dota 2](https://en.wikipedia.org/wiki/OpenAI_Five). This is frustrating.

Now, I know a simple person is unable to use complex algorithms such as OpenAI's Five (at least nowadays). It requires a really powerful hardware in order to deal with so much data, especially because it uses LSTMs instead of Conv2Ds(like Serpent's DQN does). However, there are more games that might be interesting to test some RL and that doesn't require that much structure. Not only that, but one could always go for some cloud computing and enjoy the advantages of borrowing 32 GPUs from a datacenter(don't forget to save your model).

Considering all of this, I refused to be at the mercy of OpenAI's goodwill and decided to embrace Serpent.

**However, SerpentAI got outdated and, with that, came some problems**

SerpentAI was first developed in 2017 and then had been abandoned in 2018. At the time, TensorFlow was still in version 1, keras didn't reach version 2(it was still just a standalone package) and so forth. Not only that, but when Brochu tried to continue developing Serpent again, in 2020, he began to make some improvements that, in the end, never got finished. If you try to dig into the code made in 2020, you'll see many #TODOs(try checking the cli.py).
Because of this, many adjustements were necessary. I've marked down the version required for some modules, like keras and scikit-image(though this one is more because I developed my plugins based on others' code), downloaded the new code for Serpent and added to my Serpent path only the ones that wouldn't break the code(like cli.py would do. Seriously, don't use cli.py unless you're a programmer and want to build it). I've also modified some code in order to remove importation errors(keras using Tensorflow backend, which triggered a Serpent Error asking to setup ML, even if you've done it already) and some others that caused specific issues(like offshoot read mode for files, which required an argument encoding='utf-8').

Then, I managed to make SerpentAI functional. And, to make your life easier, I've compiled the changed files and uploaded them into this repository.

**PLEASE READ THIS IN ORDER TO UPDATE YOUR SERPENT FILES AND AVOID TRACEBACK ERRORS**

You'll proceed to do everything Nicholas Brochu tells you to do [in this video](https://www.youtube.com/watch?v=5d4Ceq1L8hg) - Which is basically the same thing that is written [in the wiki](https://github.com/SerpentAI/SerpentAI/wiki)

Then, follow these steps:

1. In the repository screen(uh...this screen, where you're probably reading this), click in "Code" ---> Download ZIP
2. Extract your zip to somewhere. **DO NOT EXTRACT IT INTO YOUR SERPENT FOLDER** if you have it open.
3. Go to the extracted folder --> site-packages.
4. Copy the 3 folders that are there(offshoot, keras, serpent).
5. Go to your conda's environment library path. Example: `C:/Program Files/Anaconda/envs/Serpent/Lib`
6. Open the folder `site-packages`
7. Paste those 3 folders you've copied there. Replace any files when asked.

**IMPORTANT:** If you call `serpent setup` or `serpent setup {module}`, you'll have to do this process again.

**IMPORTANT2:** If you, like me, are NOT a badass programmer, do not do anything more than that, **especially trying to use cli.py**

If you run into any errors, open an issue in the `Issues` tab and I'll see what I can do. But try googling first. You'll probably find answers from people that know more than me.


## ~~Update: Revival (May 2020)~~

Development work has resumed on the framework with the aim of bringing it into 2020: Python 3.8+, Less Dependencies, Ease of Use (Installer, GUI) and much more! Still open-source with a permissive license and looking into a Steam distribution for non-technical users. 🐍

## ~~Warning: End of life (November 2018)~~

Serpent.AI is a simple yet powerful, novel framework to assist developers in the creation of game agents. Turn ANY video game you own  into a sandbox environment ripe for experimentation, all with familiar Python code. The framework's _raison d'être_ is first and foremost to provide a valuable tool for Machine Learning & AI research. It also turns out to be ridiculously fun to use as a hobbyist (and dangerously addictive; a fair warning)!

The framework features a large assortment of supporting modules that provide solutions to commonly encountered scenarios when using video games as environments  as well as CLI tools to accelerate development. It provides some useful conventions but is absolutely NOT opiniated about what you put in your agents: Want to use the latest, cutting-edge deep reinforcement learning algorithm? ALLOWED. Want to use computer vision techniques, image processing and trigonometry? ALLOWED. Want to randomly press the Left or Right buttons? _sigh_ ALLOWED. To top it all off, Serpent.AI was designed to be entirely plugin-based (for both game support and game agents) so your experiments are actually portable and distributable to your peers and random strangers on the Internet.

Serpent.AI supports Linux, Windows ~~& macOS~~.

_The next version of the framework will officially stop supporting macOS. Apple's aversion to Nvidia in their products means no recent macOS machine can run CUDA, an essential piece of technology for Serpent.AI's real-time training. Other decisions like preventing 32-bit applications from running in Catalina and deprecating OpenGL do not help make a case to support the OS._ 

![](https://s3.ca-central-1.amazonaws.com/serpent-ai-assets/demo_isaac.gif)

_Experiment: Game agent learning to defeat Monstro (The Binding of Isaac: Afterbirth+)_

## Background

The project was born out of admiration for / frustration with [OpenAI Universe](https://github.com/openai/universe). The idea is perfect, let's be honest, but some implementation details leave a lot to be desired. From these, the core tennets of the framework were established:

1. Thou shall run natively. Thou shalt not use Docker containers or VNC servers.
2. Thou shall allow a user to bring their own games. Thou shalt not wait for licensing deals and special game APIs.
3. Thou shall encourage diverse and creative approaches. Thou shalt not only enable AI flavors of the month.

_Want to know more about how Serpent.AI came to be? Read [The Story Behind Serpent.AI](http://blog.serpent.ai/the-story-behind-serpent-ai/) on the blog!_

## Documentation

Guides, tutorials and videos are being produced and added to the [GitHub Wiki](https://github.com/SerpentAI/SerpentAI/wiki). It currently is the official source of documentation.

![](https://s3.ca-central-1.amazonaws.com/serpent-ai-assets/demo_ymbab.gif)

_Experiment: Game agent learning to match tiles (You Must Build a Boat)_

_Business Contact: info@serpent.ai_
