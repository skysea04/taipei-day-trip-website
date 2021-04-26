// 登入註冊相關
const toSignBtn = document.querySelector('#to-sign')
const signBg = document.querySelector('.sign-bg')
const signCloseBtns = signBg.querySelectorAll('.close-btn')
const signContainers = document.querySelectorAll('.sign-container')

function popUpSignField(){
    signBg.classList.add('pop-up')
    toSignBtn.classList.add('active')
}
function cancelPopUpSignField(){
    signBg.classList.remove('pop-up')
    toSignBtn.classList.remove('active')
}

function changeSignContainer(){
    signContainers.forEach(container=>{
        container.classList.toggle('show')
    })
}

toSignBtn.addEventListener('click', popUpSignField)

signCloseBtns.forEach(btn => {
    btn.addEventListener('click',cancelPopUpSignField)
})

signBg.addEventListener('click', e => {
    if(e.path[0] === signBg){
        cancelPopUpSignField()
    }
})

signContainers.forEach(container => {
    const changeBtn = container.querySelector('p')
    changeBtn.addEventListener('click', changeSignContainer)
})