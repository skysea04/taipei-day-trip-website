// fetch景點api

//行程訂購元素
const bookingInfo = document.querySelector('.booking-info')
const imgContainer = bookingInfo.querySelector('.img-container')
const imgIndex = bookingInfo.querySelector('.img-index')
const profile = bookingInfo.querySelector('.profile')

//景點資訊元素
const info = document.querySelector('.info')
const addressContainer = info.querySelector('.address')
const transportContainer = info.querySelector('.transport')



const attractionID = document.URL.slice(-1);
const apiUrl = '/api/attraction/' + attractionID
const fetchAttraction = async () => {
    const result = await fetch(apiUrl)
    const data = await result.json()
    const attraction = data.data

    console.log(attraction)

    //寫入images 和 indexes
    const imgUrls = attraction.images
    imgUrls.forEach(imgUrl => {
        const img = document.createElement('img')
        const index = document.createElement('div')
        img.src = imgUrl
        imgContainer.append(img)
        imgIndex.append(index)
    })
    const firstImg = imgContainer.querySelector('img')
    const firstIndex = imgIndex.querySelector('div')
    firstImg.classList.add('show')
    firstIndex.classList.add('show')

    //寫入profile 名稱 類別、捷運站
    const attractionName = document.createElement('h3')
    const category = document.createElement('p')
    attractionName.innerText = attraction.name
    category.innerText = `${attraction.category} at ${attraction.mrt}`
    profile.insertAdjacentElement('afterbegin', category)
    profile.insertAdjacentElement('afterbegin', attractionName)

    //寫入info 景點資訊
    const description = document.createElement('p')
    const address = document.createElement('p')
    const transport = document.createElement('p')
    description.innerText = attraction.description
    address.innerText = attraction.address
    transport.innerText = attraction.transport

    info.insertAdjacentElement('afterbegin', description)
    addressContainer.append(address)
    transportContainer.append(transport)
}

fetchAttraction()
    .then(() => {
        // 景點圖片互動輪播功能
        const imgs = document.querySelectorAll('.img-container img')
        const indexBoxes = document.querySelectorAll('.img-index div')
        const preBtn = document.querySelector('#pre-btn')
        const nextBtn = document.querySelector('#next-btn')
        const changeTime = 5000
        
        const imgCount = imgs.length //圖片數量
        let currentImgIndex = 0
        let preImgIndex = imgCount - 1
        let nextImgIndex = currentImgIndex + 1
        
        //找到現在呈現圖片的索引
        function findCurrentImg(){
            for(let i = 0; i < imgCount; i++){
                if(imgs[i].className.includes('show')){
                    currentImgIndex = i
                    preImgIndex = ( i===0 ? imgCount-1 : i-1)
                    nextImgIndex = ( i === imgCount-1 ? 0 : i+1)
                }
            }
        }
        
        //更換圖片
        function changeImg(index){
            imgs[index].classList.toggle('show')
            indexBoxes[index].classList.toggle('show')
            imgs[currentImgIndex].classList.toggle('show')
            indexBoxes[currentImgIndex].classList.toggle('show')
            findCurrentImg()
        }
        
        //上一張
        function showPreImg(){
            changeImg(preImgIndex)
        }
        //下一張
        function showNextImg(){
            changeImg(nextImgIndex)
        }
        //自動播放
        let autoChangeImg = window.setInterval(showNextImg, changeTime)
        
        preBtn.addEventListener('click',()=>{
            showPreImg()
            clearInterval(autoChangeImg)
            autoChangeImg = window.setInterval(showNextImg, changeTime)
        })
        nextBtn.addEventListener('click',()=>{
            showNextImg()
            clearInterval(autoChangeImg)
            autoChangeImg = window.setInterval(showNextImg, changeTime)
        })
    })
        
        