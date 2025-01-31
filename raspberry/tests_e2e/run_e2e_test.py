from time import sleep
from threading import Thread

from unittest import TestCase

from src.robot import Robot
from src.robot.instructions import Instruction
from src.robot.utils import Utils as utils
from src.robot.config import Config as config


TEST_COUNT = 1


def run_e2e_test(testing_class: TestCase, tile_events: list[tuple[int, int, bool]], instructions: list[Instruction], test_name: str = "NAME NOT SPECIFIED") -> None:

    global TEST_COUNT

    # config.PRINT_LOGS = False

    if config.PRINT_LOGS:
        print()
        print(f"|--- TEST {'%-5s' % f'[{TEST_COUNT}]:'} {test_name}:")
        TEST_COUNT += 1

    robot_tile_events = utils.create_robot_tile_events(tile_events)
    robot = Robot(robot_tile_events)
    robot.instruction_manager.update_instructions(instructions)
    
    arm = robot.tile_manager._arm

    error = None

    def testing_func():
        
        nonlocal error

        sleep(config.E2E_TESTING_START_TIMEOUT)
        sleep(config.SCANNER_TILE_EVENT_TIMEOUT)
        
        for tile_event in tile_events:
            sleep(tile_event[0])
            try:
                testing_class.assertEqual(tile_event[2], arm.has_pushed())
            except AssertionError as e:
                robot.stop(log=False)
                robot.logs.print()

                error = e
                return

        robot.stop()

    robot_thread = Thread(target=robot.run)
    testing_thread = Thread(target=testing_func)

    robot_thread.start()
    testing_thread.start()

    testing_thread.join()
    testing_thread.join()

    if error is not None:
        raise error
