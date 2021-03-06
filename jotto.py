"""
Fun little ai to help pick words for the game jotto
Author: Benjamin Gutierrez
Date: 3/19/2020
"""





class Jotto:
    def __init__(self):
        # keeps track of the remaining jotto words
        self.words = Jotto.getJottoWords()
        self.allWords = set(self.words)
        self.wordLength = None
        self.keptLetters = set()
        self.removedLetters = set()
        self.guesses = {} # {guess1:numMatches1,...}

    @staticmethod
    def getJottoWords():
        """ Gets words from scrabble word file, and returns valid jotto words"""
        filename = "scrabble_words.txt"
        fileHandle = open(filename, "r") # open filename read only
        scrabbleWords = []
        for line in fileHandle:
            word = line.strip()
            word = word.lower()
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
        self.words = set(newWords)
        self.allWords = set(self.words)
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
                currentLetters = Jotto.wordToSet(currentWord)
                if currentLetters.intersection(letters) == set():
                    newWords.append(currentWord)
            self.words = set(newWords)
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
        self.words = set(newWords)

        #-----
        # By this point we have kept all words that have a combination of valid letters
        # now see if we can remove words by seeing if there are any letters
        # we can figure out
        self.guesses[word] = numMatches
        self.trimLetters()
        return

    def updateKeptRemovedLetters(self):
        """ updates self.keptLetters and self.removedLetters """
        alphabetString = "abcdefghijklmnopqrstuvwxyz"
        alphabet = Jotto.wordToSet(alphabetString)

        self.removedLetters = set(alphabet)
        self.keptLetters = set(alphabet)
        for letter in alphabet:
            for word in self.words:
                if letter in word:
                    self.removedLetters.discard(letter)
                else: # letter not in word
                    self.keptLetters.discard(letter)
        return None

    def trimLetters(self):
        """ Find letters that are either in or not in all remaining words """
        self.updateKeptRemovedLetters()

        for guess, numMatches in self.guesses.items():
            lettersInGuess = Jotto.wordToSet(guess)

            # letters than are known to be kept
            lettersMatching = lettersInGuess.intersection(self.keptLetters)
            numLettersMatching = len(lettersMatching)
            
            # letters than are known to be removed
            lettersNotMatching = lettersInGuess.intersection(self.removedLetters)
            numLettersNotMatching = len(lettersNotMatching)

            # if all letters are known to be matching, all other letters should be removed
            if numLettersMatching == numMatches:
                # remove remaining letters
                lettersToRemove = lettersInGuess - lettersMatching
                self.removeLetters(lettersToRemove)

            if numLettersNotMatching == self.wordLength - numMatches:
                lettersToKeep = lettersInGuess - lettersNotMatching
                self.keepLetters(lettersToKeep)

        # for each pair of guess, see if there are differences between the number of matches
        # that can tell us if there are letters we should remove or keep
        for guess1, numMatches1 in self.guesses.items():
            for guess2, numMatches2 in self.guesses.items():
                # skip guess if guess is itself
                if guess1 == guess2:
                    continue

                # too many possiblities to deal with equal number of matches
                if numMatches1 == numMatches2:
                    continue

                letters1 = Jotto.wordToSet(guess1)
                letters2 = Jotto.wordToSet(guess2)
                lettersIntersection = letters1.intersection(letters2)
                numIntersecting = len(lettersIntersection)
                differenceInMatches = numMatches2 - numMatches1

                # difference in matches + number of intersecting == wordLength
                # means difference is due to discrepancy in letters that should be kept or removed
                if numIntersecting == self.wordLength - abs(differenceInMatches):
                    # keep non-intersecting letters in match 2 and remove non-intersecting letters in match 1
                    lettersToKeep = None
                    lettersToRemove = None
                    if numMatches2 > numMatches1:
                        lettersToKeep = letters2 - lettersIntersection
                        lettersToRemove = letters1 - lettersIntersection
                    else: #numMatches1 > numMatches2
                        lettersToKeep = letters1 - lettersIntersection
                        lettersToRemove = letters2 - lettersIntersection
                    self.keepLetters(lettersToKeep)
                    self.removeLetters(lettersToRemove)       
        return
            

    def removeLetters(self, lettersToRemove):
        """ Removes words in self.words that have letters in lettersToRemove

            Parameters:
            lettersToRemove (set): set of 1 character strings that represent
                                the letter to be removed from self.words

            Returns:
            None
        """
        newWords = set(self.words)
        for word in self.words:
            for letter in lettersToRemove:
                if letter in word:
                    newWords.discard(word)
        self.words = set(newWords)
        self.updateKeptRemovedLetters()
        return

    def keepLetters(self, lettersToKeep):
        """ Only keeps words in self.words that have letters in lettersToKeep

            Parameters:
            lettersToRemove (set): set of 1 character strings that represent
                                the letter to be keep from self.words

            Returns:
            None
        """
        newWords = set(self.words)
        for word in self.words:
            for letter in lettersToKeep:
                if letter not in word:
                    newWords.discard(word)     
        self.words = set(newWords)
        self.updateKeptRemovedLetters()
        return
        
            
            
        

    
    def playGame(self):
        """ Run this function to play the game """
        print("Welcome to jotto AI")
        self.getNumberOfLetters()

        print("")
        print('If word is unknown, type "unknown"')
        print('To print the remaining words, type "remaining"')
        print('When game is over, type "game over"')
        
        gameOver = False
        numMoves = 0
        while (gameOver == False):
            gameOver = self.takeGuess()
            numMoves += 1
            print("Words left: " + str(len(self.words)))
        print("Congratulations. Total moves: " + str(numMoves))
        return

    def calculateGuess(self, scenario):
        """ Returns the optimal guess based on a particular scenario

        Parameters:
        scenario (string): the type of scenario to calculate the optimal guess
                            must be either "worst" or "average"

        Returns:
        (string): If scenario is "worst", returns the guess that gives the largest elimination
                    of jotto words in the worst case number of matches
                  If scenario is "average", returns the guess that gives the largest elimination
                    of jotto words in the average case number of matches
        """
        # back up rep invariant
        self.wordsBackup = set(self.words)
        self.allWordsBackup = set(self.allWords)
        self.wordLengthBackup = int(self.wordLength)
        self.keptLettersBackup = set(self.keptLetters)
        self.removedLettersBackup = set(self.removedLetters)
        self.guessesBackup = dict(self.guesses) # [(guess1,numMatches1),...]

        
        numInitialWords = len(self.words)
        guessesToTry = set()
        numGuesses = 100
        for _ in range(numGuesses):
            guess = self.allWords.pop()
            if guess in self.guesses: # (word, numMatches)
                continue
            else:
                guessesToTry.add( guess )
        self.allWords = set(self.allWordsBackup)

        # find word counts for scenario after elimination
        wordCounts = {} 
        for word in guessesToTry:
            
            workingWordCount = [] # list of word counts after elimination
            for numMatches in range(0,self.wordLength+1):
            # restore rep invariant for next trial
                self.words = set(self.wordsBackup)
                self.allWords = set(self.allWordsBackup)
                self.wordLength = int(self.wordLengthBackup)
                self.keptLetters = set(self.keptLettersBackup)
                self.removedLetters = set(self.removedLettersBackup)
                self.guesses = dict(self.guessesBackup) # [(guess1,numMatches1),...]
                
                self.pickWord(word, numMatches)
                numRemainingWords = len(self.words)
                workingWordCount.append(numRemainingWords)
                
            # pick word count based on scenario
            wordCount = None
            if scenario == "worst":
                wordCount = max(workingWordCount)
            elif scenario == "average":
                wordCount = int( sum(workingWordCount)/len(workingWordCount) )
            else:
                raise ValueError('parameter scenario must be either "worst" or "average"')

            wordCounts[word] = wordCount

        # best guess has lowest word count for scenario after elimination
        bestGuess = min(wordCounts, key=wordCounts.get)

        # restore rep invariant
        self.words = set(self.wordsBackup)
        self.allWords = set(self.allWordsBackup)
        self.wordLength = int(self.wordLengthBackup)
        self.keptLetters = set(self.keptLettersBackup)
        self.removedLetters = set(self.removedLettersBackup)
        self.guesses = dict(self.guessesBackup) # [(guess1,numMatches1),...]
        return bestGuess
            
        
            
            

    def takeGuess(self, guess=None):
        """ Takes a guess, returns True if game is over, else returns False """
        
        if guess==None:
            try:
                #guess = self.calculateGuess("average")
                if len(self.words) < 500:
                    guess = self.calculateGuess("worst")
                    #guess = self.words.pop()
                else:
                    guess = self.words.pop()
            except KeyError: # game over
                return True
            self.words.add(guess)

        print("")
        print("Guess the word: " + guess)

        numMatches = self.getNumberOfMatches()
            
        if type(numMatches) == list and numMatches[0] == "guess":
            userGuess = numMatches[1]
            if len(userGuess) == self.wordLength and userGuess in self.allWords:
                guess = userGuess
                return self.takeGuess(guess)
            else:
                print("Invalid guess")
                return self.takeGuess(guess)

        if type(numMatches) == list and numMatches[0] == "remove":
            lettersToRemove = numMatches[1]
            self.removeLetters(lettersToRemove)
            return self.takeGuess()

        if type(numMatches) == list and numMatches[0] == "keep":
            lettersToKeep = numMatches[1]
            self.keepLetters(lettersToKeep)
            return self.takeGuess()

        if numMatches == "new":
            return self.takeGuess()
        
        if numMatches == "unknown":
            self.words.discard(guess)
            return self.takeGuess()
            
        if numMatches == "game over":
            return True
        
        self.pickWord(guess, numMatches)
        self.words.discard(guess)
        if len(self.words) ==0: # game over
            return True
        
        return False

        
                
                
    def getNumberOfMatches(self):
        """ Helper function for playGame """
        print("How many matches: " )
        try:
            userInput = input()

            if userInput == "list":
                print("Remaining words")
                print(self.words)
                return self.getNumberOfMatches()

            if userInput == "remaining":
                print("Keep letters: " + str(sorted(list(self.keptLetters))))
                print("Remove letters: " + str(sorted(list(self.removedLetters))))
                print("Words left: " + str(len(self.words)))
                return self.getNumberOfMatches()


            if type(userInput) == str and len(userInput) >= 5 and userInput[0:5] == "guess":
                return userInput.split()

            if type(userInput) == str and len(userInput) >= 6 and userInput[0:6] == "remove":
                splittedInput = userInput.split()
                lettersToRemove = splittedInput[1]
                if len(lettersToRemove) >= 26 - self.wordLength:
                    print(lettersToRemove)
                    raise IOError
                return splittedInput

            if type(userInput) == str and len(userInput) >= 4 and userInput[0:4] == "keep":
                splittedInput = userInput.split()
                lettersToKeep = splittedInput[1]
                if len(lettersToKeep) > self.wordLength:
                    raise IOError
                return splittedInput
            
            if userInput == "unknown":
                return userInput

            if userInput == "count":
                return userInput

            if userInput == "new":
                return userInput
            
            if userInput == "game over":
                return userInput
            numMatches = int(userInput)
            minMatches = 0
            maxMatches = self.wordLength
            if minMatches <= numMatches and numMatches <= maxMatches:     
                return numMatches
            else:
                raise IOError
        except (IOError, ValueError, IndexError) as e:
            print('That did not work. Please enter a number between 0 and ' + str(self.wordLength) + ' or type "game over".')
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
