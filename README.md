# AstRobotPh
Neural network to generate journal paper titles, with twitter bot.

Twitter bot at https://twitter.com/astrobotph .

The neural network used is the one in "Generative Deep Learning: Teaching Machines to Paint, Write, Compose and Play" by David Foster, 06_01_lstm_text_train.ipynb (That code is used to train the network and not given here.) https://github.com/davidADSP/GDL_code

Python notebooks:
1. PaperTitleDataMining.ipynb // 
Notebook to create training data of astrophysics paper titles from the ArXiv website, through their API.

2. PaperTitleGeneratorPreTrained.ipynb // 
Test notebook to see how to run the pre-trained network to generate a new title, and explore string manipulation.

Twitterbot:
Files in the folder "AstRobotPhTwitter" are those needed to deploy the bot on Heroku cloud server. Bot generates and tweets a random paper title a few times a day and can reply to tweets, generating a new title starting with words given in double quotes.
