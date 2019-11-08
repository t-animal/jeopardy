const lunchpad = require('lunchpad');
var ks = require('node-key-sender');

const Color = lunchpad.Color;

const generateBlankSquare = require('lunchpad/src/lib/generateBlankSquare');



const keys = ['a', 'b', 'c', 'd']

async function init() {
  const launchpads = []

  try {
    await lunchpad.initialize(1).then(launchpad => launchpads.push(launchpad));
    await lunchpad.initialize(2).then(launchpad => launchpads.push(launchpad));
    await lunchpad.initialize(3).then(launchpad => launchpads.push(launchpad));
    await lunchpad.initialize(4).then(launchpad => launchpads.push(launchpad));
  }catch(e) {
    console.log(launchpads.length + ' Boards found'); 
  }

  return launchpads;
}

let isCleared = false
function clearAllBoards(launchpads) {
  launchpads.forEach(elem => {
    elem.updateBoard(generateBlankSquare(Color.GREEN))
    elem.clearSquares()
  })
  isCleared = true
}

init().then((boards) => {
  clearAllBoards(boards);
  buttons(boards);
})


function buttons(launchpads) {

  launchpads.forEach(elem => {
    elem.on('input', () => {buttonPressed(elem)})
  })

  function buttonPressed(button) {
    if(!isCleared){
      return;
    }

    ks.sendKey(keys[launchpads.indexOf(button)]);

    button.updateBoard(generateBlankSquare(Color.GREEN))
    isCleared = false;

    const nextRound = () => {
      clearAllBoards(launchpads);
      button.removeListener('functionX', nextRound)
      button.removeListener('functionY', nextRound)
    }
    button.on('functionX', nextRound)
    button.on('functionY', nextRound)

    launchpads.forEach(elem => {
      if (elem === button) return;
      elem.updateBoard(generateBlankSquare(Color.RED))
    })
  }

}


module.exports = init;