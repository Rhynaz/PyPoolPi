from logging import LogRecord
from queue import Empty, Full, Queue
from textwrap import dedent

from flask import Blueprint, Response

from core.controller_interface import CoverState
from utils.log import add_log_emitted_callback, remove_log_emitted_callback

from ..flask_app import get_flask_app

EVENTS = Blueprint("events", __name__, url_prefix="/events")


@EVENTS.get("/")
def stream_events():
    config_manager = get_flask_app().config_manager
    controller = get_flask_app().controller
    config = config_manager.config.http.event_stream
    event_queue = Queue(maxsize=config.queue_size)

    def state_changed(_old_state: CoverState, new_state: CoverState) -> None:
        try:
            event_queue.put_nowait(
                dedent(f"""
                    event: state
                    data: {new_state.name}
                """).strip()
            )
        except Full:
            pass

    def config_changed(*_args) -> None:
        try:
            event_queue.put_nowait(
                dedent("""
                    event: config
                    data:
                """).strip()
            )
        except Full:
            pass

    def log_emitted(_record: LogRecord, line: str) -> None:
        try:
            event_queue.put_nowait(
                dedent(f"""
                    event: log
                    data: {line}
                """).strip()
            )
        except Full:
            pass

    def event_generator():
        controller.add_cover_state_changed_callback(state_changed)
        config_manager.add_config_changed_callback(config_changed)
        add_log_emitted_callback(log_emitted)

        try:
            yield ": ok\n\n"
            while True:
                try:
                    yield event_queue.get(timeout=config.keep_alive_interval) + "\n\n"
                except Empty:
                    yield ": keep alive\n\n"
        except GeneratorExit:
            pass

        controller.remove_cover_state_changed_callback(state_changed)
        config_manager.remove_config_changed_callback(config_changed)
        remove_log_emitted_callback(log_emitted)

    return Response(event_generator(), mimetype="text/event-stream")
