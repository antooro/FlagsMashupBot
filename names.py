import re
import random

TOOBIG = -1
TOOSMALL = -2
NOTNEW = -3
EMPTY = -1


class NameJoiner:
    def __init__(self, str1, str2):
        words = [str1, str2]
        random.shuffle(words)
        self.fullStartName = words[0]
        self.fullEndName = words[1]
        self.initVariables()

    def initVariables(self):
        self.lower_limit = min(len(self.fullStartName), len(self.fullEndName))
        self.upper_limit = max(len(self.fullStartName), len(self.fullEndName)) + self.lower_limit - 1
        self.firstPositions = self.getKeyVocalsPositions(self.fullStartName)
        self.secondPositions = self.getKeyVocalsPositions(self.fullEndName)

    def join(self):

        res = self.tryToJoin()
        if res == -1:
            self.fullStartName, self.fullEndName = self.fullEndName, self.fullStartName
            self.initVariables()
            res = self.tryToJoin()

        if res == -1:
            self.initVariables()
            return self.fullStartName+self.fullEndName[self.secondPositions[-1]+1:]

        return res

    def tryToJoin(self):

        firstSplitPlace = self.chooseRandomFirstSplit()
        secondSplitPlace = NOTNEW
        while secondSplitPlace < 0:
            secondSplitPlace = self.chooseRandomSecondSplit(firstSplitPlace)

            if secondSplitPlace < 0:
                self.handleErrorWithFirstPlace(
                    secondSplitPlace, firstSplitPlace)
                firstSplitPlace = self.chooseRandomFirstSplit()
                if firstSplitPlace == EMPTY:
                    return EMPTY

            else:
                namex = self.fullStartName[:firstSplitPlace] + \
                    self.fullEndName[secondSplitPlace:]
                if namex in [self.fullStartName, self.fullEndName]:
                    self.secondPositions = [
                        i for i in self.secondPositions if i != secondSplitPlace-1]
                    if len(self.secondPositions) == 0:
                        self.secondPositions = self.getKeyVocalsPositions(
                            self.fullEndName)
                        self.firstPositions = self.erasePlaceEq(
                            firstSplitPlace)
                        firstSplitPlace = self.chooseRandomFirstSplit()
                        if firstSplitPlace == EMPTY:
                            return EMPTY

                    secondSplitPlace = NOTNEW

        return self.fullStartName[:firstSplitPlace] + self.fullEndName[secondSplitPlace:]

    def handleErrorWithFirstPlace(self, error, firstSplitPlace):
        if error == TOOBIG:  # Need smaller first part
            self.firstPositions = self.erasePlacesGreaterEq(firstSplitPlace)

        elif error == TOOSMALL:  # Need greater first part
            self.firstPositions = self.erasePlacesLowerEq(firstSplitPlace)

    def erasePlaceEq(self, position):
        p = position - 1
        res = [i for i in self.firstPositions if i != p]

        return res

    def erasePlacesLowerEq(self, position):
        p = position - 1
        res = [i for i in self.firstPositions if i > p]

        return res

    def erasePlacesGreaterEq(self, position):
        p = position - 1
        res = [i for i in self.firstPositions if i < p]

        return res

    def chooseRandomFirstSplit(self):

        if len(self.firstPositions) == 0:
            print(
                f"{self.fullStartName} has been omitted while trying to join with {self.fullEndName}")
            return -1
        pos = random.choice(self.firstPositions) + 1

        return pos

    def getKeyVocalsPositions(self, s):
        regex_iter = re.finditer(r'[aeiouy][^aeiou]', s.lower())
        positions = [i.start() for i in regex_iter]
        return positions

    def chooseRandomSecondSplit(self, firstSplitPlace):

        minimumCharactersLeft = self.lower_limit - firstSplitPlace
        maximumCharactersLeft = self.upper_limit - firstSplitPlace

        minimumIndex = len(self.fullEndName) - maximumCharactersLeft
        maximumIndex = len(self.fullEndName) - minimumCharactersLeft

        filtered_big_positions = [
            i for i in self.secondPositions if i <= maximumIndex]
        if len(filtered_big_positions) == 0:
            return -2
        filtered_positions = [
            i for i in self.secondPositions if minimumIndex <= i + 1 <= maximumIndex]
        if len(filtered_positions) == 0:
            return -1

        return random.choice(filtered_positions) + 1
