function setWordColors() 
{
    alert("Set word colors for " + knownWords);
    $('#scrollableWindow span').each(function(index, element) 
    {
        var word = $(element).text().trim();
        var colorClass = getColorClass(word);
        $(element).removeClass('green red black').addClass(colorClass);
    });
}

function getColorClass(word) 
{
    if (knownWords.includes(word.toLowerCase())) {return 'green';} else {return 'red';}
}

function insertIntoChat() 
{
    const userInput = textInput.value;
    fetch('/insertIntoChat', 
    {
        method: 'POST',
        headers: {'Content-Type': 'application/json',},
        body: JSON.stringify({ text: userInput }),
    })
    .then(response => response.text())
    .then(result => 
    {
        const scrollableWindow = document.getElementById("scrollableWindow");
        scrollableWindow.innerHTML += result;
        scrollableWindow.scrollTop = scrollableWindow.scrollHeight; // Scroll to the bottom            
        textInput.value = "";
    })
    .then(result =>
    {
        setWordColors();
    });
}

function getSelectedWord() 
{
    var text = window.getSelection().toString().trim();
    return text;
}

function insertWordNotes(word, response2) 
{
    try
    {
        selectedWord.text(word);
        selectedWordNotes.val(response2);
        addKnownWord(word);
    }
    catch (error) {alert(error);}
}

function addKnownWord(word)
{
    if (!knownWords.includes(word.toLowerCase()))
    {
        knownWords = knownWords.concat(word);
        setWordColors();
    }
}
