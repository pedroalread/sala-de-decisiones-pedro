from playwright.sync_api import sync_playwright
from pathlib import Path
import json
URL="https://pedroalread.github.io/sala-de-decisiones-pedro/"
results=[]
def ck(n,ok):results.append((n,bool(ok)));print(("PASS" if ok else "FAIL"),n,flush=True)
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,args=["--no-sandbox","--disable-dev-shm-usage"])
 for w,h in [(2560,1440),(1920,1080),(390,844),(320,700)]:
  context=b.new_context(viewport={"width":w,"height":h},accept_downloads=True);page=context.new_page();errors=[];page.on("pageerror",lambda err:errors.append(str(err)))
  response=page.goto(URL,wait_until="domcontentloaded",timeout=60000)
  ck(f"{w} HTTP 200",response.status==200)
  ck(f"{w} three choices",page.locator(".s-case").count()==3)
  ck(f"{w} no JS errors",not errors)
  ck(f"{w} no overflow",page.evaluate("document.documentElement.scrollWidth<=innerWidth"))
  if w==2560:
   page.locator("#evaluate").click()
   ck("Mortgage analysis",page.locator("#decision-result").is_visible())
   ck("Evidence non-empty",len(page.locator("#result-evidence").inner_text())>20)
   with page.expect_download() as d:page.locator("#export-result").click()
   ck("JSON download",d.value.suggested_filename.endswith(".json"))
   page.locator("#reset-result").click();ck("Reset",page.locator("#decision-result").is_hidden())
   page.locator(".s-case button").nth(1).click()
   ck("Payments loaded","POS" in page.locator("#scenario-title").inner_text())
   page.locator("input[name=choice][value='2']").check();page.locator("#evaluate").click()
   ck("Payments third decision",page.locator("#result-risk").inner_text()!="")
   page.locator(".s-case button").nth(2).click()
   ck("Savings loaded","Adopción" in page.locator("#scenario-title").inner_text())
   page.locator("#evaluate").click()
   ck("Savings analysis",page.locator("#decision-result").is_visible())
   ck("Portfolio contact links",page.locator('a[href^="mailto:pedro18@gmail.com"]').count()>=2)
   page.screenshot(path="qa/qhd.png",full_page=False)
  if w==390:page.screenshot(path="qa/movil.png",full_page=False)
  context.close()
 b.close()
n=sum(t[1] for t in results);Path("qa/resultado.json").write_text(json.dumps({"passed":n,"total":len(results),"tests":results},ensure_ascii=False,indent=2));print(f"RESULT: {n}/{len(results)} passing");assert n==len(results)
