import logging
import random
from logging import Logger
from typing import Optional, Dict, List

import yaml
from playwright.sync_api import sync_playwright, Page, Browser, ElementHandle

SECOND: int = 1000
WAIT_TIME: int = int(SECOND * 1.5)

logger: Logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


def handle_exceptions(fn):
    from functools import wraps

    @wraps(fn)
    def wrapper(self, *args, **kw):
        try:
            return fn(self, *args, **kw)
        except Exception as e:
            logger.debug(f"Failed to proceed on selector {args[0]} with error {e}")
            catch_error: bool = kw.get("catch_error", False)
            if not catch_error:
                raise e

    return wrapper


@handle_exceptions
def wait_and_click(
        page: Page, selector: str, timeout: Optional[int] = None, catch_error: bool = False
):
    page.wait_for_selector(selector, timeout=timeout)
    target: Optional[ElementHandle] = page.query_selector(selector)
    target.click(timeout=timeout)


@handle_exceptions
def fill_text(
        page: Page,
        selector: str,
        text: str,
        timeout: Optional[int] = None,
        catch_error: bool = False,
):
    page.wait_for_selector(selector, timeout=timeout)
    page.query_selector(selector).fill(text, timeout=timeout)


@handle_exceptions
def quiz_random_answer(page: Page, catch_error: bool = False):
    all_buttons: List[ElementHandle] = page.query_selector_all(".Quiz_circle__1vNJh")
    answer_check_button: Optional[ElementHandle] = page.query_selector(
        ".Quiz_cardWrapper__OWFUa .Quiz_card__19K9G .pointer"
    )
    next_quiz_button: Optional[ElementHandle] = page.query_selector(
        ".Quiz_cardWrapper__OWFUa .Quiz_button__28dQe"
    )
    if all_buttons:
        next_button: ElementHandle = random.choice(all_buttons)
        next_button.click(timeout=WAIT_TIME)

    if answer_check_button:
        answer_check_button.click(timeout=WAIT_TIME)

    if next_quiz_button:
        next_quiz_button.click(timeout=WAIT_TIME)


@handle_exceptions
def mute_video(page: Page, catch_error: bool = False):
    # find video and mute
    video: Optional[ElementHandle] = page.query_selector("video")
    if video:
        page.evaluate("video => video.muted = true", video)


def login(page: Page, **kwargs):
    page.goto("https://www.yebigun.or.kr/")
    notify_popup_sel: str = ".final-noty-modal-wrapper .pcititle .pointer"
    wait_and_click(page, notify_popup_sel)
    class_start_btn_sel: str = ".ClassHandler_startClass__1ek7A.BoxContainer_btn__1ZusC"
    wait_and_click(page, class_start_btn_sel)
    notice_check_sel: str = ".agree-wrapper .InputCheckbox_check_box_effect__2F99R"
    wait_and_click(page, notice_check_sel)
    notice_check_btn_sel: str = (
        ".mandatory-warning-wrapper .btn.checked.BoxContainer_btn__1ZusC"
    )
    wait_and_click(page, notice_check_btn_sel)

    fill_text(page, """.input-wrapper-top > input[placeholder*="이름"]""", kwargs["name"])
    fill_text(
        page, """.input-wrapper-top > input[placeholder*="생년월일"]""", kwargs["birth"]
    )
    fill_text(
        page, """.input-wrapper-bottom > input[placeholder*="군번"]""", kwargs["mil_num"]
    )

    login_btn_sel: str = ".login > .login-text-box.BoxContainer_btn__1ZusC"
    wait_and_click(page, login_btn_sel)

    fill_text(
        page,
        ".LoginComponent_inputWrapper__XYGNE input.enPwOnly",
        kwargs["password"],
        catch_error=True,
    )
    wait_and_click(page, ".LoginComponent_pwBtn__629ig")


def process_with_infinite_clicks(page: Page):
    wait_and_click(
        page,
        ".HomeTitle_bottomWrapper__2mRno .BoxContainer_root__1ClvP.BoxContainer_btn__1ZusC",
    )
    wait_and_click(
        page,
        ".VideoList_classHandlerWrapper__2vkYu .ClassHandler_startClass__1ek7A.BoxContainer_btn__1ZusC",
    )

    while True:
        wait_and_click(
            page,
            ".openModal.modal .boxcontainer.BoxContainer_btn__1ZusC",
            timeout=WAIT_TIME,
            catch_error=True,
        )
        mute_video(page, catch_error=True)
        wait_and_click(
            page,
            ".SummaryBottom_root__1Mjlg .boxcontainer.BoxContainer_btn__1ZusC",
            timeout=WAIT_TIME,
            catch_error=True,
        )
        quiz_random_answer(page, catch_error=True)


def run():
    with sync_playwright() as p:
        browser: Browser = p.firefox.launch(headless=False)
        pg: Page = browser.new_page()

        config: Dict = yaml.safe_load(open("config.yml", mode="r", encoding="utf-8"))

        login(pg, **config)
        process_with_infinite_clicks(pg)


if __name__ == "__main__":
    run()
