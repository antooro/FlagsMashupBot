import requests
import random
from PIL import Image
from collections import Counter
from names import NameJoiner
from bs4 import BeautifulSoup
import os
import shutil
import cairosvg
import sqlite3
import itertools
import math


class CountryMixer:
    def rgb2hex(self, color):
        r, g, b = color
        code = "#{:02x}{:02x}{:02x}".format(r, g, b)
        return code

    def smallerHex(self, bigHex):
        smaller = "#"
        for i in [1, 3, 5]:
            smaller += bigHex[i]
        return smaller

    def getCountry(self, code):
        for n in self.flags_info:
            if n['alpha2Code'] == code:
                country = n
        print(country['name'])
        return country

    def getNeighbours(self):
        hasCountries = False
        while not hasCountries:
            first_country = random.choice(self.flags_info)

            country_flag_code = first_country['alpha3Code']
            print(country_flag_code, first_country['borders'])
            if len(first_country['borders']) > 0:
                frontier = random.choice(first_country['borders'])
                for flag_info in self.flags_info:
                    if flag_info['alpha3Code'] == frontier:
                        second_country = flag_info

                if first_country and second_country:
                    hasCountries = True

        self.first_country = first_country
        self.second_country = second_country
        self.countries = (self.first_country, self.second_country)
        for country in self.countries:
            self.downloadPNGFlag(country["alpha3Code"])

    def updateDbWithBase(self, template):
        conn = sqlite3.connect('countries.db')
        c = conn.cursor()
        first_country, second_country = sorted(
            [self.first_country['alpha2Code'], self.second_country['alpha2Code']])

        c.execute('update countries set base=(?) where first_country=(?) and second_country=(?) and base is null',
                  (template, first_country, second_country))
        conn.commit()

    def insertCountries(self):
        conn = sqlite3.connect('countries.db')
        c = conn.cursor()
        first_country, second_country = sorted(
            [self.first_country['alpha2Code'], self.second_country['alpha2Code']])
        print(first_country, second_country)
        c.execute('insert into countries values (?,?,?)',
                  (first_country, second_country, None))
        conn.commit()

    def isAlreadyDone(self, template, colors):
        conn = sqlite3.connect('countries.db')
        c = conn.cursor()
        first_country, second_country = sorted([template, colors])
        c.execute("select * from countries where first_country=? and second_country=? and base=?",
                  (first_country, second_country, template))
        rows = c.fetchall()

        return len(rows) != 0

    def checkMashupValid(self):
        conn = sqlite3.connect('countries.db')
        c = conn.cursor()
        first_country, second_country = sorted(
            [self.first_country['alpha2Code'], self.second_country['alpha2Code']])
        if first_country == "NU" or second_country == "NU":
            return False
        print(first_country, second_country)
        c.execute('select * from countries where first_country=? and second_country=?',
                  (first_country, second_country))
        rows = c.fetchall()
        print(rows)
        if len(rows) == 1 and rows[0][2]:
            co = Counter(rows[0])
            self.template3Code = co.most_common()[-1][0]
            if self.template3Code == self.first_country['alpha2Code']:
                self.template3Code = self.first_country['alpha3Code']
            else:
                self.template3Code = self.second_country['alpha3Code']
            print(self.template3Code)
            return True
        elif len(rows) < 1:
            self.template3Code = None

            return True
        else:
            self.template3Code = None

            return False

    def getFullFlagsInfoJSON(self):
        info = requests.get("https://restcountries.eu/rest/v2/all")
        if info.status_code != 200:
            raise RuntimeError("Can't get full flags info")

        return info.json()

    def chooseRandomFlag(self, alreadyChoosen=None):

        while True:
            flag = random.choice(self.flags_info)
            if flag['alpha3Code'] != alreadyChoosen:
                return flag

    def downloadPNGFlag(self, alpha3Code):
        r = requests.get(
            f"https://restcountries.eu/data/{alpha3Code.lower()}.svg")
        print(alpha3Code)
        cairosvg.svg2png(bytestring=r.text,
                         write_to=f'{alpha3Code.lower()}.png')

    def randomlyDownloadFlags(self):

        self.first_country = self.chooseRandomFlag()
        self.second_country = self.chooseRandomFlag()
        self.countries = (self.first_country, self.second_country)

        for country in self.countries:
            self.downloadPNGFlag(country["alpha3Code"])

    def getFlagsEmojis(self):
        emojis = []

        for country in self.countries:
            country_alpha_code = country['alpha2Code']
            emoji = (chr(
                ord(country_alpha_code[0]) + 127397) + chr(ord(country_alpha_code[1]) + 127397))
            emojis.append(emoji)

        return emojis

    def getFlagsSortedColors(self):

        flagsSortedColors = []

        for country in self.countries:
            img = Image.open(f'{country["alpha3Code"].lower()}.png')
            width, height = img.size
            limit = ((width * height) * .01)
            colors = img.convert('RGBA').getcolors(
                img.size[0] * img.size[1])  # this converts the mode to RGB
            colors = sorted(colors, key=lambda x: x[0], reverse=True)
            colors = [c for c in colors if c[1][3] != 0]

            colorb1 = [self.rgb2hex(color[1][:3])
                       for color in colors[:5] if color[0] > limit]

            combinations = itertools.combinations(colorb1, 2)

            for pair in combinations:
                r1, g1, b1 = tuple(int(pair[0].replace("#", "")[
                                       i:i + 2], 16) for i in (0, 2, 4))
                r2, g2, b2 = tuple(int(pair[1].replace("#", "")[
                                       i:i + 2], 16) for i in (0, 2, 4))
                dif = math.sqrt(math.pow(r1 - r2, 2) +
                                math.pow(g1 - g2, 2) + math.pow(b1 - b2, 2))
                if dif < 50 and pair[1] in colorb1:
                    print(pair)
                    colorb1.remove(pair[1])
            print(colorb1)
            print("\n")
            flagsSortedColors.append(colorb1)
        return flagsSortedColors

    def selectTemplateAndColors(self, nameColorList):

        FIRSTCOUNTRY = NAME = 0
        LASTCOUNTRY = COLORS = 1

        template = nameColorList[FIRSTCOUNTRY][NAME]
        colors = nameColorList[LASTCOUNTRY][NAME]

        if len(nameColorList[FIRSTCOUNTRY][COLORS]) > len(nameColorList[LASTCOUNTRY][COLORS]):
            template, colors = colors, template

        elif len(nameColorList[FIRSTCOUNTRY][COLORS]) == len(nameColorList[LASTCOUNTRY][COLORS]):
            if random.randint(0, 2) == 0:
                template, colors = colors, template

            if self.isAlreadyDone(self.countries[template]["alpha2Code"], self.countries[colors]["alpha2Code"]):
                template, colors = colors, template

            if self.first_country is not self.second_country:
                self.updateDbWithBase(self.countries[template]["alpha2Code"])

        if not self.template3Code:
            self.template3Code = self.countries[template]['alpha3Code']
        templateSVG = requests.get(
            f"https://restcountries.eu/data/{self.template3Code.lower()}.svg")

        for i in nameColorList:

            if i[NAME] == colors:
                newColors = i[COLORS]
            else:
                oldColors = i[COLORS]

        if self.first_country == self.second_country:
            newColors = reversed(newColors)

        colorsDict = dict(zip(newColors, oldColors))

        return templateSVG.text, colorsDict

    def clean(self, text):
        colors_file = open("colors", "r")
        color_codes = colors_file.readlines()
        color_codes = [code.split(",") for code in color_codes]
        clean = {}
        for code in color_codes:
            code = code[0].split()
            clean[code[0].lower()] = code[1].replace("\n", "")

        data2 = text
        for key, value in clean.items():
            tag = f'fill="{key}"'

            if tag in data2:
                new_value = f'fill="{value}"'
                print(tag, new_value)
                data2 = data2.replace(tag, new_value)
            tag = f'fill:{key}'

            if tag in data2:
                new_value = f'fill:{value}'
                print(tag, new_value)
                data2 = data2.replace(tag, new_value)

        if data2 is not text:
            print("They differ")
            text = data2

        root = BeautifulSoup(text, "lxml")
        svg = root.find("svg")

        svg_rects = svg.findAll('rect', recursive=False)
        differs = False
        for t in svg_rects:
            fill = t.get("fill")

            if fill is None and t.get("style") is None and t.get("stroke") is None:
                t['fill'] = "#000000"
                differs = True

        svc_paths = svg.findAll('path', recursive=False)

        for t in svc_paths:
            fill = t.get("fill")

            if fill is None and t.get("style") is None and t.get("stroke") is None:
                t['fill'] = "#000000"
                differs = True

        if differs:
            print("They differ")
            data = str(svg).replace("<html><body>",
                                    "\n").replace("</body></html>", "")
            text = data

        return text

    def changeColors(self, changes):
        self.svgText = self.clean(self.svgText)
        for new, old in changes.items():
            self.svgText = self.svgText.replace(old, new.replace('#', 'ç'))
            self.svgText = self.svgText.replace(
                old.upper(), new.replace('#', 'ç'))

        for new, old in changes.items():
            self.svgText = self.svgText.replace(
                self.smallerHex(old), new.replace('#', 'ç'))
            self.svgText = self.svgText.replace(
                self.smallerHex(old).upper(), new.replace('#', 'ç'))

        self.svgText = self.svgText.replace('ç', '#')

    def calculateNames(self):
        name1 = self.first_country['name']
        name2 = self.second_country['name']

        if "(" in name1:
            p_temp = name1.split("(")
            name1 = p_temp[1].replace(")", "") + " " + p_temp[0]

        if "(" in name2:
            p_temp = name2.split("(")
            name2 = p_temp[1].replace(")", "") + " " + p_temp[0]

        if "," in name1:
            p_temp = name1.split(", ")
            name1 = p_temp[1] + " " + p_temp[0]

        if "," in name2:
            p_temp = name2.split(", ")
            name2 = p_temp[1] + " " + p_temp[0]

        self.first_country['name'] = name1
        self.second_country['name'] = name2

        if len(name2.split()) > 1:
            name = (" ".join(name2.split()[:-1]) + " " + name1.split()[-1])
        elif len(name1.split()) > 1:
            name = (" ".join(name1.split()[:-1]) + " " + name2.split()[-1])
        else:
            name = NameJoiner(
                self.first_country['name'], self.second_country['name']).join()
        if name1 == name2:
            name = name1 + " 2"
        return name

    def saveToPNG(self):
        image = Image.open(f'{self.template3Code.lower()}.png')
        width, height = image.size
        uploaded = False
        bigger = max(width, height, 4096)
        limit_kb = 3072

        while not uploaded:
            cairosvg.svg2png(bytestring=self.svgText,
                             write_to='output.png', scale=int(4096 / bigger))
            fileSize = os.stat("output.png").st_size / 1024
            if fileSize < limit_kb:
                uploaded = True
            else:
                bigger = bigger * 1.25

    def mixFlags(self):

        colorb1, colorb2 = self.getFlagsSortedColors()

        print(colorb1, len(colorb1))
        print(colorb2, len(colorb2))

        template, colors = self.selectTemplateAndColors(
            [(0, colorb1), (1, colorb2)])
        self.svgText = template
        self.changeColors(colors)
        self.saveToPNG()

    def removePNGs(self):
        i = 1
        for country_data in self.countries:
            try:
                filePath = f'{country_data["alpha3Code"].lower()}.png'
                flagPath = f'flag{i}.png'
                i = i + 1
                shutil.move(filePath, flagPath)
            except:
                print("Unable to delete", filePath)

    def manuallyDownloadFlags(self, alpha3CodeFlag1=None, alpha3CodeFlag2=None):
        if not alpha3CodeFlag1:
            self.first_country = self.chooseRandomFlag()
        else:
            self.first_country = self.getCountry(alpha3CodeFlag1)

        if not alpha3CodeFlag2:
            self.second_country = self.chooseRandomFlag()
        else:
            self.second_country = self.getCountry(alpha3CodeFlag2)

        self.countries = (self.first_country, self.second_country)

        self.downloadPNGFlag(self.first_country["alpha3Code"])
        self.downloadPNGFlag(self.second_country["alpha3Code"])

    def main(self):
        self.flags_info = self.getFullFlagsInfoJSON()
        correct_country = False
        while not correct_country:
            randomNum = random.randrange(4)
            if randomNum == 0:
                self.getNeighbours()
            else:
                self.randomlyDownloadFlags()
            # self.manuallyDownloadFlags()

            correct_country = self.checkMashupValid()

        self.insertCountries()
        self.mixFlags()
        print("Base is " + self.template3Code)
        print(self.first_country['alpha3Code'],
              self.second_country['alpha3Code'])
        name = self.calculateNames()
        print(name)

        self.removePNGs()
        return [self.first_country["name"], self.second_country["name"]], self.getFlagsEmojis(), name


c = CountryMixer()
c.main()
