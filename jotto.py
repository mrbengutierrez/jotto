"""
Fun little ai to help pick words for the game jotto
Author: Benjamin Gutierrez
Date: 3/19/2020
"""


import random


class Jotto:
    def __init__(self):
        # keeps track of the remaining jotto words
        self.words = Jotto.getJottoWords()
        self.wordLength = None

    @staticmethod
    def getJottoWords():
        """ Gets words from scrabble word file, and returns valid jotto words"""
        filename = "scrabble_words.txt"
        fileHandle = open(filename, "r") # open filename read only
        scrabbleWords = []
        for line in fileHandle:
            word = line.strip()
            scrabbleWords.append(word)
        jottoWords = []
        for word in scrabbleWords:
            if Jotto.isJottoWord(word):
                jottoWords.append(word)
        return set(jottoWords)

    def keepWordsOfLength(self, wordLength):
        """ Keeps all jotto words of a certain word length
            Modifies the jotto word list
            Parameters:
            wordLength (int): length of word, must be >0
            Returns:
            None
        """
        newWords = []
        for word in self.words:
            if len(word) == wordLength:
                newWords.append(word)
        self.words = newWords
        return

    def pickWord(self, word, numMatches):
        """ Shrinks self.words such as to only keep words that
            could possibly have the number of letter matches given
            Parameters:
            word (string): word to shrink
            numMatches (int): number of letter matches
                              ( 0 <= nuMatches <= len(word) )
            Returns:
            None
        """
        # set of letters in word
        letters = Jotto.wordToSet(word)

        # remove words that have any letters in word if
        # there are no matches
        if numMatches == 0:
            newWords = []
            for currentWord in self.words:
                for letter in currentWord:
                    if letter not in letters:
                        newWords.append(currentWord)
            self.words = newWords
            return

        #else there are some matches
        allLetterCombinations = Jotto.getLetterCombinations(word)

        # only keep letter combinations that are of length of number of matches
        letterCombinations = []
        for letterCombination in allLetterCombinations: 
            if len(letterCombination) == numMatches:
                letterCombinations.append(letterCombination)

        # check if there is a letter combination in word
        newWords = []
        for currentWord in self.words:
            for letterCombination in letterCombinations:
                if Jotto.isCombinationInWord(letterCombination, currentWord):
                    newWords.append(currentWord)
                    break
        self.words = newWords
        return

    
    def playGame(self):
        """ Run this function to play the game """
        print("Welcome to jotto AI")
        self.getNumberOfLetters()

        print("")
        print('When game is over, type "game over"')
        gameOver = False
        numMoves = 0
        while (gameOver == False):
            guess = random.choice(self.words)
            print("")
            print("Guess the word: " + guess)
            numMatches = self.getNumberOfMatches()
            if numMatches == "game over":
                gameOver = True
                break
            self.pickWord(guess, numMatches)
            numMoves += 1
            print("Words left: " + str(len(self.words)))
        print("Congratulations. Total moves: " + str(numMoves))
        
        
                
                
    def getNumberOfMatches(self):
        """ Helper function for playGame """
        print("How many matches: " )
        try:
            userInput = input()

            if userInput == "remaining":
                print("Remaining words")
                print(self.words)
                return self.getNumberOfMatches()
            
            if userInput == "game over":
                return userInput
            numMatches = int(userInput)
            return numMatches
        except (IOError, ValueError) as e:
            print('That did not work. Please enter a number between 0 and ' + str(self.wordLength) + 'or type "game over".')
            return self.getNumberOfMatches()
            
                  
                  


       


    def getNumberOfLetters(self):
        """ Helper function for playGame """
        print("How many letters is jotto word: ")
        try:
            numLetters = int( input() )
            
            minLetters = 2
            maxLetters = 15
            if minLetters <= numLetters and numLetters <= maxLetters:
                self.keepWordsOfLength(numLetters)
                self.wordLength = numLetters
                return
            else:
                raise IOError
        except (IOError, ValueError) as e:
            print("That did not work. Please enter a number between 2 and 15")
            self.getNumberOfLetters()
        
        

    
                
                
            
        

    @staticmethod
    def isCombinationInWord(letterCombination, word):
        """ Returns true if a validjotto letter combination is contained in
            a valid jotto word, else returns False
            Parameters:
            letterCombination (list): a list of characters representing a letter combination.
                                        all characters must be unique
            word (string): the word. all characters must be unique
            Returns:
            (bool): True if all letters of letterCombination are contained in word
        """
        letterCombinationSet = set(letterCombination)
        letterSet = Jotto.wordToSet(word)
        if letterCombinationSet.issubset(letterSet):
            return True
        return False
                  
        
        
            
    @staticmethod
    def getLetterCombinations(word):
        letters = [letter for letter in word]
        letters.sort()
        letterCombinations = []
        Jotto._getLetterCombinationsHelper(letters, 0, [], letterCombinations)
        return letterCombinations
        
    @staticmethod
    def _getLetterCombinationsHelper(inputArray, pos, charList, letterCombinations):
        """ Recursively computes the letter combinations for a sorted array of letters
            Parameters:
            inputArray (list): sorted array of letters
            pos (int): integer specifing current position in charList.
                        initialized as 0
            charList (list): next working combination starting list.
                            initialized as []
            letterCombinations (list): return parameter
                            A working list of all of the letter combinations
                            for a sorted array of letters. Will be a full list
                            of all of the letter combinations on the final
                            recursive step.
                            initialized as []
                            
            Returns:
            None
            """
        for i in range(pos, len(inputArray)):
            if (i != pos and inputArray[i] == inputArray[i-1]):
                continue
            charList.append(inputArray[i])
            letterCombinations.append(charList.copy())
            Jotto._getLetterCombinationsHelper(inputArray, i+1,charList, letterCombinations)
            del charList[-1]
        
        

    @staticmethod
    def isJottoWord(word):
        """Returns true if word is a valid jotto word, else returns false"""
        letters = set()
        for letter in word:
            if letter in letters:
                return False
            letters.add(letter)
        return True

    @staticmethod
    def wordToSet(word):
        """Converts a word to a set of lettters in the word
            Parameters:
            word (string): word to be converted
            Returns:
            (set): set of letters in word
        """
        letterSet = set()
        for letter in word:
            letterSet.add(letter)
        return letterSet
        
        
        
        
        



def main():
    J = Jotto()
    J.playGame()
                  
    
    









if __name__ == "__main__":
    main()
