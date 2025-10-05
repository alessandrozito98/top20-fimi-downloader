from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import pandas as pd
import re
import os, sys
import tkinter as tk
from tkinter import simpledialog, filedialog

URL = "https://www.fimi.it/top-of-the-music/classifiche/"

def resource_path(rel_path: str) -> str:
    try:
        base = sys._MEIPASS  # cartella temporanea quando è un eseguibile onefile
    except Exception:
        base = os.path.dirname(__file__)
    return os.path.join(base, rel_path)

def ask_top_n_and_save(df: pd.DataFrame) -> None:
    root = tk.Tk()
    root.withdraw()
    n = simpledialog.askinteger("Quante righe", "Quante vuoi (1–100)?",
                                parent=root, minvalue=1, maxvalue=100)  # [web:142]
    if not n:
        root.destroy()
        return
    df_out = df.sort_values("posizione").head(n).copy()
    path = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                        filetypes=[("Excel","*.xlsx"), ("CSV","*.csv")])  # [web:146]
    if path:
        if path.lower().endswith(".xlsx"):
            df_out.to_excel(path, index=False)
        else:
            df_out.to_csv(path, index=False, encoding="utf-8")
    root.destroy()

def scrape_singoli(url: str) -> pd.DataFrame:
    opts = webdriver.ChromeOptions()
    opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1400,2200")

    service = Service(executable_path=resource_path("chromedriver/chromedriver"))
    driver = webdriver.Chrome(service=service, options=opts)

    try:
        driver.get(url)
        a_singoli = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//ul//li[a[contains(., 'Singoli')]]/a"))
        )
        href = a_singoli.get_attribute("href")
        panel_id = href.split("#", 1)[1]
        try:
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", a_singoli)
            a_singoli.click()
        except Exception:
            pass
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, f'#{panel_id} td[data-column="Titolo"]'))
        )
        soup = BeautifulSoup(driver.page_source, "html.parser")
    finally:
        driver.quit()

    panel = soup.select_one(f"#{panel_id}")
    if panel is None:
        raise RuntimeError("Pannello Singoli non trovato; verificare l'href del tab.")

    table = panel.select_one("table")
    if table is None:
        raise RuntimeError("Tabella dei Singoli non trovata nel pannello selezionato.")

    rows = []
    for tr in table.select("tbody tr"):
        sp_pos = tr.select_one('td[data-column="Posizione"] span')
        td_tit = tr.select_one('td[data-column="Titolo"]')
        td_lab = tr.select_one('td[data-column="LAbel / Distributore"], td[data-column="Label / Distributore"]')
        if not (sp_pos and td_tit and td_lab):
            continue
        sp_text = sp_pos.get_text(strip=True)
        m = re.search(r"\d+", sp_text)
        posizione = int(m.group()) if m else None
        ta = [t.strip() for t in td_tit.get_text(separator="\n").split("\n") if t.strip()]
        brano = ta[0] if ta else ""
        artista = " ".join(ta[1:]) if len(ta) > 1 else ""
        ld = [t.strip() for t in td_lab.get_text(separator="\n").split("\n") if t.strip()]
        et_prod = ld[0] if ld else ""
        et_dist = " ".join(ld[1:]) if len(ld) > 1 else ""
        if posizione is not None:
            rows.append({
                "posizione": posizione,
                "brano": brano,
                "artista": artista,
                "etichetta produttrice": et_prod,
                "etichetta distributrice": et_dist
            })
    df = pd.DataFrame(rows).sort_values("posizione").reset_index(drop=True)
    return df

if __name__ == "__main__":
    df_singoli = scrape_singoli(URL)  # DataFrame della Top 100 Singoli [web:113]
    ask_top_n_and_save(df_singoli)    # Dialog per scegliere quante righe e salvare [web:146]
    print(df_singoli.head(10))
