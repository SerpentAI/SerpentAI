from serpent.game_agent import GameAgent
import collections
from serpent.input_controller import KeyboardKey
import serpent.utilities
from serpent.sprite_locator import SpriteLocator
import numpy as np
from datetime import datetime
from serpent.frame_grabber import FrameGrabber
import skimage.color
import skimage.measure
import serpent.cv
import serpent.utilities
import serpent.ocr

import time

from serpent.input_controller import KeyboardEvent, KeyboardEvents
from serpent.input_controller import MouseEvent, MouseEvents

from serpent.config import config

from serpent.analytics_client import AnalyticsClient


class Environment:

    def __init__(self, name, game_api=None, input_controller=None):
        self.name = name

        self.game_api = game_api
        self.input_controller = input_controller

        self.game_state = dict()

        self.analytics_client = AnalyticsClient(project_key=config["analytics"]["topic"])

        self.reset()

    @property
    def episode_duration(self):
        return time.time() - self.episode_started_at

    @property
    def episode_over(self):
        if self.episode_maximum_steps is not None:
            return self.episode_steps >= self.episode_maximum_steps
        else:
            return False

    @property
    def new_episode_data(self):
        return dict()

    @property
    def end_episode_data(self):
        return dict()

    def new_episode(self, maximum_steps=None, reset=False):
        self.episode_steps = 0
        self.episode_maximum_steps = maximum_steps

        self.episode_started_at = time.time()

        if not reset:
            self.episode += 1

        self.analytics_client.track(
            event_key="NEW_EPISODE",
            data={
                "episode": self.episode,
                "episode_data": self.new_episode_data,
                "maximum_steps": self.episode_maximum_steps
            }
        )

    def end_episode(self):
        self.analytics_client.track(
            event_key="END_EPISODE",
            data={
                "episode": self.episode,
                "episode_data": self.end_episode_data,
                "episode_steps": self.episode_steps,
                "maximum_steps": self.episode_maximum_steps
            }
        )

    def episode_step(self):
        self.episode_steps += 1
        self.total_steps += 1

        self.analytics_client.track(
            event_key="EPISODE_STEP",
            data={
                "episode": self.episode,
                "episode_step": self.episode_steps,
                "total_steps": self.total_steps
            }
        )

    def reset(self):
        self.total_steps = 0

        self.episode = 0
        self.episode_steps = 0

        self.episode_maximum_steps = None

        self.episode_started_at = None

    def update_game_state(self, game_frame):
        raise NotImplementedError()

    def perform_input(self, actions):
        discrete_keyboard_keys = set()
        discrete_keyboard_labels = set()

        for label, game_input, value in actions:
            # Discrete Space
            if value is None:
                if len(game_input) == 0:
                    discrete_keyboard_labels.add(label)
                    continue

                for game_input_item in game_input:
                    if isinstance(game_input_item, KeyboardEvent):
                        if game_input_item.event == KeyboardEvents.DOWN:
                            discrete_keyboard_keys.add(game_input_item.keyboard_key)
                            discrete_keyboard_labels.add(label)

        discrete_keyboard_keys_sent = False

        for label, game_input, value in actions:
            # Discrete
            if value is None:
                # Discrete - Keyboard
                if (len(discrete_keyboard_keys) == 0 and len(discrete_keyboard_labels) > 0) or isinstance(game_input[0] if len(game_input) else None, KeyboardEvent):
                    if not discrete_keyboard_keys_sent:
                        self.input_controller.handle_keys(list(discrete_keyboard_keys))

                        self.analytics_client.track(
                            event_key="GAME_INPUT",
                            data={
                                "keyboard": {
                                    "type": "DISCRETE",
                                    "label": " - ".join(sorted(discrete_keyboard_labels)),
                                    "inputs": sorted([keyboard_key.value for keyboard_key in discrete_keyboard_keys])
                                },
                                "mouse": {}
                            }
                        )

                        discrete_keyboard_keys_sent = True
                # Discrete - Mouse
                elif isinstance(game_input[0], MouseEvent):
                    for event in game_input:
                        if event.event == MouseEvents.CLICK:
                            self.input_controller.click(button=event.button)
                        elif event.event == MouseEvents.CLICK_DOWN:
                            self.input_controller.click_down(button=event.button)
                        elif event.event == MouseEvents.CLICK_UP:
                            self.input_controller.click_up(button=event.button)
                        elif event.event == MouseEvents.CLICK_SCREEN_REGION:
                            screen_region = event.kwargs["screen_region"]
                            self.input_controller.click_screen_region(button=event.button, screen_region=screen_region)
                        elif event.event == MouseEvents.SCROLL:
                            self.input_controller.scroll(direction=event.direction)

                        self.analytics_client.track(
                            event_key="GAME_INPUT",
                            data={
                                "keyboard": {},
                                "mouse": {
                                    "type": "DISCRETE",
                                    "label": label,
                                    "label_technical": event.as_label,
                                    "input": event.as_input,
                                    "value": value
                                }
                            }
                        )
            # Continuous
            else:
                if isinstance(game_input[0], KeyboardEvent):
                    self.input_controller.tap_keys(
                        [event.keyboard_key for event in game_input],
                        duration=value
                    )

                    self.analytics_client.track(
                        event_key="GAME_INPUT",
                        data={
                            "keyboard": {
                                "type": "CONTINUOUS",
                                "label": label,
                                "inputs": sorted([event.keyboard_key.value for event in game_input]),
                                "duration": value
                            },
                            "mouse": {}
                        }
                    )
                elif isinstance(game_input[0], MouseEvent):
                    for event in game_input:
                        if event.event == MouseEvents.CLICK_SCREEN_REGION:
                            screen_region = event.kwargs["screen_region"]
                            self.input_controller.click_screen_region(button=event.button, screen_region=screen_region)
                        elif event.event == MouseEvents.MOVE:
                            self.input_controller.move(x=event.x, y=event.y)
                        elif event.event == MouseEvents.MOVE_RELATIVE:
                            self.input_controller.move(x=event.x, y=event.y, absolute=False)
                        elif event.event == MouseEvents.DRAG_START:
                            screen_region = event.kwargs.get("screen_region")
                            coordinates = self.input_controller.ratios_to_coordinates(value, screen_region=screen_region)

                            self.input_controller.move(x=coordinates[0], y=coordinates[1], duration=0.1)
                            self.input_controller.click_down(button=event.button)
                        elif event.event == MouseEvents.DRAG_END:
                            screen_region = event.kwargs.get("screen_region")
                            coordinates = self.input_controller.ratios_to_coordinates(value, screen_region=screen_region)

                            self.input_controller.move(x=coordinates[0], y=coordinates[1], duration=0.1)
                            self.input_controller.click_up(button=event.button)

    def clear_input(self):
        self.input_controller.handle_keys([])


import gc

from serpent.machine_learning.reinforcement_learning.agents.rainbow_dqn_agent import RainbowDQNAgent


import enum


class InputControlTypes(enum.Enum):
    DISCRETE = 0
    CONTINUOUS = 1


class SerpentTenshi2GameAgent(GameAgent):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.frame_handlers["PLAY"] = self.handle_play

        self.frame_handler_setups["PLAY"] = self.setup_play

        self.game_state = None

        self._reset_game_state()

    def _reset_game_state(self):
        self.game_state = {
            "hp": collections.deque(np.full((8,), 4), maxlen=8),
            "power": collections.deque(np.full((8,), 1), maxlen=8),
            "aura": collections.deque(np.full((8,), 100), maxlen=8),
            "score_multiplier": collections.deque(np.full((8,), 1.00), maxlen=8),
            "score": collections.deque(np.full((8,), 0), maxlen=8),
            "run_reward": 0,
            "current_run": 1,
            "current_run_steps": 0,
            "current_run_hp": 0,
            "current_run_power": 0,
            "curent_run_aura": 0,
            "current_run_score_mult": 0,
            "current_run_score": 0,
            "run_predicted_actions": 0,
            "last_run_duration": 0,
            "record_time_alive": dict(),
            "random_time_alive": None,
            "random_time_alives": list(),
            "run_timestamp": datetime.utcnow(),
        }


    def setup_play(self):
        
        
        '''input_mapping = {
            "UP": [KeyboardKey.KEY_UP],
            "DOWN": [KeyboardKey.KEY_DOWN],
            "LEFT": [KeyboardKey.KEY_LEFT],
            "RIGHT": [KeyboardKey.KEY_RIGHT],
            #"UP-LEFT": [KeyboardKey.KEY_UP, KeyboardKey.KEY_LEFT, KeyboardKey.KEY_Z],
            #"UP-RIGHT": [KeyboardKey.KEY_UP, KeyboardKey.KEY_RIGHT, KeyboardKey.KEY_Z],
            #"DOWN-LEFT": [KeyboardKey.KEY_DOWN, KeyboardKey.KEY_LEFT, KeyboardKey.KEY_Z],
            #"DOWN-RIGHT": [KeyboardKey.KEY_DOWN, KeyboardKey.KEY_RIGHT, KeyboardKey.KEY_Z],
            "Shoot" : [KeyboardKey.KEY_Z],
            "Aura": [KeyboardKey.KEY_X]
        }'''
    
        self.game_inputs = [
            {
                "name": "CONTROLS",
                "control_type": InputControlTypes.DISCRETE,
                "inputs": self.game.api.combine_game_inputs(["MOVEMENT", "SHOOTING"])
            }
        ]


        #network_spec = [{"type": "conv2d", "size": 2}, {'type': 'dense', 'size': 20}]

        self.agent = RainbowDQNAgent("Tenshi", game_inputs=self.game_inputs)
        
        
        
        #self.agent.add_human_observations_to_replay_memory()
        

    '''def setup_play_local(self):
        context_classifier_path = 'C:/Users/giova/SerpentAI/plugins/SerpentTenshi2GameAgentPlugin/files/ml_models/context_classifier.model'
        context_classifier = CNNInceptionV3ContextClassifier(input_shape=(1920, 1080, 3))
        context_classifier.prepare_generators()
        context_classifier.load_classifier(context_classifier_path)
        self.machine_learning_models['context_classifier'] = context_classifier'''   


    def handle_play(self, game_frame):
        
        #self._reset_game_state()
        
        gc.disable()
        
        import pyautogui
        pyautogui.press('z')
        
        #context = self.machine_learning_models['context_classifier'].predict(game_frame.game)

        hp = self._measure_hp(game_frame)
        power = self._measure_power(game_frame)
        aura = self._measure_aura(game_frame)
        mult_score = self._measure_mscore(game_frame)
        score = self._measure_score(game_frame)

        self.game_state['hp'].appendleft(hp)
        self.game_state['power'].appendleft(power)
        self.game_state['aura'].appendleft(aura)
        self.game_state['score_multiplier'].appendleft(mult_score)
        self.game_state['score'].appendleft(score)

        reward = self._reward(self.game_state, game_frame)
        if reward is None:
            reward = 0
        else:
            pass

        self.game_state['run_reward'] = reward
        
        
        self.agent.observe(reward=reward)
        
        frame_buffer = FrameGrabber.get_frames([0, 2, 4, 6], frame_type="PIPELINE")
        agent_actions = self.agent.generate_actions(frame_buffer)

        Environment.perform_input(self, actions=agent_actions)

        # Saving model each N steps:
        if self.agent.current_step % 5000 == 0:
            self.agent.save_model()

        
        serpent.utilities.clear_terminal()
        print(f"Current HP: {self.game_state['hp'][0]}")
        print(f"Current Power: {self.game_state['power'][0]}")
        print(f"Current Aura: {self.game_state['aura'][0]}")
        print(f"Current Score: {self.game_state['score'][0]}")
        print(f"Current Score Multiplier: {self.game_state['score_multiplier'][0]}")
        print(f"Current Reward: {self.game_state['run_reward']}")
        
            
    def _measure_hp(self, game_frame):
        area = serpent.cv.extract_region_from_image(game_frame.frame, self.game.screen_regions['Lifes'])

        hp = 0
        max_ssim = 0
        for name, sprite in self.game.sprites.items():
            for i in range(sprite.image_data.shape[3]):
                ssim = skimage.measure.compare_ssim(area, np.squeeze(sprite.image_data[..., :3, i]), multichannel=True)
                    
                if ssim > max_ssim:
                    max_ssim = ssim
                    hp = int(name[-1])
                        
                    return hp

    def _measure_score(self, game_frame):
        score_area_frame = serpent.cv.extract_region_from_image(game_frame.frame, self.game.screen_regions["Score"])
            
        score_grayscale = np.array(skimage.color.rgb2gray(score_area_frame) * 255, dtype="uint8")
            
        score = serpent.ocr.perform_ocr(image=score_grayscale, scale=10, order=5, horizontal_closing=10, vertical_closing=5)
            
        self.game_state['current_run_score'] = score

        return score

    def _measure_power(self, game_frame):
        score_area_frame = serpent.cv.extract_region_from_image(game_frame.frame, self.game.screen_regions["Power"])
            
        score_grayscale = np.array(skimage.color.rgb2gray(score_area_frame) * 255, dtype="uint8")
            
        score = serpent.ocr.perform_ocr(image=score_grayscale, scale=10, order=5, horizontal_closing=10, vertical_closing=5)
            
        self.game_state['current_run_power'] = score

        return score
        
    def _measure_aura(self, game_frame):
        score_area_frame = serpent.cv.extract_region_from_image(game_frame.frame, self.game.screen_regions["Aura"])
            
        score_grayscale = np.array(skimage.color.rgb2gray(score_area_frame) * 255, dtype="uint8")
            
        score = serpent.ocr.perform_ocr(image=score_grayscale, scale=10, order=5, horizontal_closing=10, vertical_closing=5)
            
        self.game_state['current_run_aura'] = score

        return score

    def _measure_mscore(self, game_frame):
        score_area_frame = serpent.cv.extract_region_from_image(game_frame.frame, self.game.screen_regions["Multiplier_score"])
            
        score_grayscale = np.array(skimage.color.rgb2gray(score_area_frame) * 255, dtype="uint8")

        score = serpent.ocr.perform_ocr(image=score_grayscale, scale=10, order=5, horizontal_closing=10, vertical_closing=5)
            
        self.game_state['current_run_score_mult'] = score

        return score


    def _reward(self, game_state, game_frame):
        if self.game_state['hp'][0] is None:
            pass
        elif self.game_state['hp'][0] >= 1.00:
            return (self.game_state['score'][0] * self.game_state['score_multiplier'][0]) + (self.game_state['power'][0] * (self.game_state['aura'][0]/100))
        else:
            return -(1000000/self.game_state['score'][0] * self.game_state['score_multiplier'][0])
  