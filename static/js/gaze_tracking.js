window.saveDataAcrossSessions = true

const LOOK_DELAY = 1000 // 1 second
const SECTION_WIDTH = window.innerWidth / 5

const CUTOFF_1 = SECTION_WIDTH
const CUTOFF_2 = SECTION_WIDTH * 2
const CUTOFF_3 = SECTION_WIDTH * 3
const CUTOFF_4 = window.innerWidth - window.innerWidth / 5

let startLookTime = Number.POSITIVE_INFINITY
let lookDirection = null
let imageElement = getNewImage()
let nextImageElement = getNewImage(true)

var video = document.getElementById("video1");

webgazer
  .setGazeListener((data, timestamp) => {
    if (data == null || lookDirection === "STOP") return

    if (data.x < CUTOFF_1 && lookDirection !== "LEFT" && lookDirection !== "RESET") {
      startLookTime = timestamp
      lookDirection = "LEFT"
    } 
    else if (data.x >= CUTOFF_2 && data.x <= CUTOFF_3 && lookDirection !== "MIDDLE" && lookDirection !== "RESET") {
      startLookTime = timestamp
      lookDirection = "MIDDLE"
    } 
    else if (data.x >= CUTOFF_4 && lookDirection !== "RIGHT" && lookDirection !== "RESET") {
      startLookTime = timestamp
      lookDirection = "RIGHT"
    }
    else if (data.x >= CUTOFF_1 && data.x <= CUTOFF_2 || data.x >= CUTOFF_3 && data.x <= CUTOFF_4) {
        startLookTime = Number.POSITIVE_INFINITY
        lookDirection = null
    }

    if (startLookTime + LOOK_DELAY < timestamp) {
        if (lookDirection === "LEFT") {
            video.pause();
        } 
        else if(lookDirection === "RIGHT") {
            video.pause();
        } 
        else if(lookDirection === "MIDDLE"){
            video.play()
        }

        startLookTime = Number.POSITIVE_INFINITY
        lookDirection = "STOP"
        setTimeout(() => {
            imageElement.remove()
            nextImageElement.classList.remove("next")
            imageElement = nextImageElement
            nextImageElement = getNewImage(true)
            lookDirection = "RESET"
        }, 200)
    }
  })
  .begin()

// webgazer.showVideoPreview(false).showPredictionPoints(false)

function getNewImage(next = false) {
  const img = document.createElement("img")
  //   document.body.append(img)
  return img
}