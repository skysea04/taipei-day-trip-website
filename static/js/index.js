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



// fetch 景點api
const searchForm = document.querySelector('.slogan form')
const main = document.querySelector('main')
const footer = document.querySelector('footer')
let page = 0
let keyword = ''

//fetch景點函式
const fetchAttractions = async () => {
    console.log('hi')
    if(page===null) return
    const result = await fetch(`/api/attractions?page=${page}&keyword=${keyword}`)
    const data = await result.json()
    const attractions = data["data"]
    for(let attr of attractions){
        // 包全部
        const attrContain = document.createElement('div')
        attrContain.classList.add('attraction')
        // 包img(還沒放網址)
        const imgContain = document.createElement('a')
        imgContain.classList.add('img-contain')
        // img本人
        const img = document.createElement('img')
        img.src = attr['images'][0]
        // 景點名稱（還沒放網址）
        const name = document.createElement('a')
        name.classList.add('name')
        name.title = attr['name']
        name.innerText = attr['name']
        // 包景點資訊
        const info = document.createElement('div')
        info.classList.add('attraction-info')
        // 捷運資訊
        const mrt = document.createElement('p')
        mrt.innerText = attr['mrt']
        // 景點類別
        const category = document.createElement('p')
        category.innerText = attr['category']

        //合併元素
        info.append(mrt, category)
        imgContain.append(img)
        attrContain.append(imgContain, name, info)
        main.append(attrContain)
    }
    page = data['nextPage']
}

//進行keyword搜尋
function fetchSearching(e){
    e.preventDefault()
    keyword = this.querySelector('input').value
    console.log(keyword)
    page = 0
    //清除main，重新fetch符合的資料
    main.innerHTML = ''
    fetchAttractions()
        .then(() => {
            let mainBottom = main.offsetHeight + main.offsetTop
            let footerTop = window.innerHeight - footer.offsetHeight
            // 當main高度不夠的時候，讓footer固定於底部
            if(mainBottom < footerTop){
                footer.classList.add('fixed-bottom')
            }else{
                footer.classList.remove('fixed-bottom')
            }
        })
}

//fetch下一頁
function renderNextPage(){
    const pageBottom = this.pageYOffset + this.innerHeight
    if(pageBottom > footer.offsetTop){
        fetchAttractions()
    }
}

// 延遲scroll

// function debounce(func, wait = 30, immediate = true) {
//     var timeout;
//     return function() {
//       var context = this, args = arguments
//       var later = function() {
//         timeout = null
//         if (!immediate) func.apply(context, args)
//       }
//       var callNow = immediate && !timeout
//       clearTimeout(timeout)
//       timeout = setTimeout(later, wait)
//       if (callNow) func.apply(context, args)
//     };
//   };

const debounce = (func, wait) => {
    let timeout;

    return function executedFunction() {
        const later = () => {
        clearTimeout(timeout);
        func();
        };

        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
};
  

// 滾動時觸發renderNextPage
window.addEventListener('scroll', debounce(renderNextPage))
// 進行keword搜尋
searchForm.addEventListener('submit', fetchSearching)

//先執行一次page=0
fetchAttractions()
