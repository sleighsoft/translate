import argparse
import os
import time

from requests import Session
from defusedxml.ElementTree import fromstring

H = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0"
}

URL = "https://dict.leo.org/dictQuery/m-vocab/esde/query.xml?lp={sl}{tl}&lang=de&search={word}&side=both&order=basic&partial=show&sectLenMax=16&n=3&filtered=-1&trigger=null"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="File with one word per line to be translated")
    parser.add_argument("srclang", help="Source language")
    parser.add_argument("tgtlang", help="Target language")
    parser.add_argument(
        "-maxwords", type=int, default=5, help="Maximum number of translations"
    )
    args = parser.parse_args()

    url = URL.format(sl=args.srclang, tl=args.tgtlang, word="{word}")
    xpath = "./sectionlist/section/entry/side/words/"

    duplicates = set()

    with open(args.file, "r", encoding="UTF-8") as f:
        lines = f.readlines()

    with open(args.file, "w", encoding="UTF-8") as f:
        with Session() as sess:
            for l in lines:
                l = l.strip()

                if l.startswith("#"):
                    continue

                splits = l.split("\t")

                if len(splits) > 1:
                    f.write(l + "\n")
                    duplicates.add(splits[0])
                    continue

                if splits[0] in duplicates:
                    continue

                data = sess.get(url.format(word=l), headers=H).text
                xml = fromstring(data)

                base = None
                translations = []

                words = xml.findall(xpath)
                if len(words) == 0:
                    f.write(f"# {l}\n")
                    continue

                for i in range(0, len(words), 2):
                    if base is None:
                        base = words[i].text
                    elif base != words[i].text:
                        break
                    translations.append(words[i + 1].text)

                duplicates.add(base)

                translations = ", ".join(translations)
                line = f"{base}\t{translations}"

                print(line)
                f.write(line + "\n")
                time.sleep(3)
