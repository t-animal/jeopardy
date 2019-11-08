const lunchpad = require('lunchpad')

const sendKey = require('./sendKey');

const Color = lunchpad.Color

const generateBlankSquare = require('lunchpad/src/lib/generateBlankSquare')

const keys = ['a', 'b', 'c', 'd']

async function init() {
  return Promise.all([
    lunchpad.initialize(1),
    lunchpad.initialize(2),
    lunchpad.initialize(3),
    lunchpad.initialize(4)
  ])
}

let isCleared = false
function clearAllBoards(launchpads) { 
  launchpads.forEach(elem => {
    // elem.updateBoard(generateBlankSquare(Color.GREEN))
    elem.clearSquares()
  })

  isCleared = true
}

init().then((boards) => {
  clearAllBoards(boards)
  buttons(boards)
})

function buttons(boards) {
  boards.forEach(elem => {
    elem.on('input', () => buttonPressed(elem))
  })

  let resetWaiting = waiting(boards)
  function buttonPressed(activeBoard) {
    if (!isCleared){
      return
    }

    resetWaiting()
    sendKey(keys[boards.indexOf(activeBoard)])

    boards.forEach(board => {
      board.updateBoard(generateBlankSquare(board === activeBoard ? Color.GREEN : Color.RED))
    });

    isCleared = false

    blinkingReset(boards, activeBoard)
  }

  function blinkingReset(boards, activeBoard) {
    activeBoard.setFunctionY(0, Color.AMBER);
  
    let on = false;
    const intervalHandle = setInterval(() => {
      activeBoard.setFunctionY(0, on ? Color.BLACK : Color.AMBER)
  
      on = !on
    }, 200)
  
    const handleReset = () => {
      clearAllBoards(boards)
      clearInterval(intervalHandle)
      activeBoard.setFunctionY(0, Color.BLACK)
      activeBoard.removeListener('functionY', handleReset)

      resetWaiting = waiting(boards)
    }
  
    activeBoard.on('functionY', handleReset)
  }

  function waiting(boards) {
    let i = 0;
    const buttons = [
      {x: 3, y: 3},
      {x: 3, y: 4},
      {x: 4, y: 4},
      {x: 4, y: 3}
    ];
  
    const intervalHandle = setInterval(() => {
      boards.forEach(board => {
        buttons.forEach(({x, y}, index) => {
          board.setSquare(x, y, index === i ? Color.BLACK : Color.AMBER);
        })
      })
  
      i = (i + 1) % buttons.length;
    }, 600);
  
    return () => {
      clearInterval(intervalHandle);
    }
  }
}



module.exports = init