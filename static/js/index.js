const signButton = document.querySelector('#to-sign')
const signBg = document.querySelector('.sign-bg')
const signCloseBtn = signBg.querySelector('.close-btn')

function popUpSignField(){
    signBg.classList.add('pop-up')
}
function cancelPopUpSignField(){
    signBg.classList.remove('pop-up')
}


signButton.addEventListener('click', popUpSignField)
signBg.addEventListener('click', cancelPopUpSignField)
signCloseBtn.addEventListener('click', cancelPopUpSignField)
