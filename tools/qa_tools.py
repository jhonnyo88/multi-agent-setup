"""
QA Tools for DigiNativa AI Agents
=================================

PURPOSE:
Verktyg som gör det möjligt för QA-agenter att interagera med en
webbläsare för att utföra end-to-end-tester och funktionell granskning.
"""
from typing import Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

class BrowserInteractionTool(BaseTool):
    name: str = "Webbläsar-interagerare"
    description: str = "Använd detta verktyg för att styra en webbläsare: öppna URL, klicka på element, fylla i fält och ta skärmdumpar."
    driver: webdriver.Chrome = None

    def __init__(self):
        super().__init__()
        # Sätt upp en "headless" Chrome-webbläsare
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(options=chrome_options)

    def _run(self, command: str, selector: str = None, value: str = None) -> str:
        """Kör ett webbläsarkommando."""
        try:
            if command == "open_url":
                self.driver.get(value)
                return f"Öppnade URL: {value}"
            elif command == "click":
                self.driver.find_element(By.CSS_SELECTOR, selector).click()
                return f"Klickade på element med selector: '{selector}'"
            elif command == "fill_text":
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                element.clear()
                element.send_keys(value)
                return f"Fyllde i texten '{value}' i elementet '{selector}'"
            elif command == "get_text":
                return self.driver.find_element(By.CSS_SELECTOR, selector).text
            elif command == "take_screenshot":
                self.driver.save_screenshot(value)
                return f"Tog skärmdump och sparade till: {value}"
            else:
                return f"Okänt webbläsarkommando: {command}"
        except Exception as e:
            return f"Ett fel uppstod i webbläsaren: {e}"

    def __del__(self):
        # Stäng webbläsaren när verktyget inte längre används
        if self.driver:
            self.driver.quit()