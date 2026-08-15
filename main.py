from argparse import ArgumentParser
from os import environ
from signal import SIG_BLOCK, SIGINT, SIGTERM, pthread_sigmask, sigwait

from config import ConfigManager
from controller import ExtensibleCoverController
from hardware import ConfigBasedHardwareAccess
from persistence import ConfigBasedPersistenceProvider
from persistence.config import ConfigFile
from presentation.http import FlaskHttpFrontend
from presentation.mqtt import PahoMqttFrontend
from utils.log import setup_log

cmdline = ArgumentParser("pypoolpi")
_ = cmdline.add_argument(
    "-c",
    "--config",
    default=environ.get("PYPOOLPI_CONFIG", "pypoolpi.config.toml"),
    dest="config_path",
    help="Path to the config file (default: pypoolpi.config.toml)",
)
args = cmdline.parse_args()

config_manager = ConfigManager()
config_file = ConfigFile(config_manager, args.config_path)

setup_log(config_manager)

persistence_provider = ConfigBasedPersistenceProvider(config_manager)
hardware_access = ConfigBasedHardwareAccess(config_manager)
cover_controller = ExtensibleCoverController(config_manager, hardware_access, hardware_access, persistence_provider)
mqtt_frontend = PahoMqttFrontend(config_manager, cover_controller)
http_frontend = FlaskHttpFrontend(config_manager, cover_controller)

signals = {SIGINT, SIGTERM}
_ = pthread_sigmask(SIG_BLOCK, signals)
_ = sigwait(signals)

http_frontend.shutdown()
mqtt_frontend.shutdown()
cover_controller.shutdown()
hardware_access.shutdown()
persistence_provider.shutdown()

config_file.shutdown()
config_manager.shutdown()
