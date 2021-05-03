//信用卡格式
const ccn = document.querySelector('#ccn'),
      cce = document.querySelector('#cce'),
      cvv = document.querySelector('#cvv')

Payment.formatCardNumber(ccn, 16);
Payment.formatCardExpiry(cce);
Payment.formatCardCVC(cvv);


//fetch user api
userAPI = '/api/user'

const headLine = document.querySelector('.headline')
function getUserData(){
    fetch(userAPI)
    .then(res => res.json())
    .then(data => {
        if(data.data != null){
            headLine.innerText = `您好，${data.data.name}，待預定的行程如下：`
        }else{
            headLine.innerText = `您尚未登入，請登入`
        }
    })
}
getUserData()

//fetch booking api
bookingAPI = '/api/booking'
const container = document.querySelector('.booking-container')

function getBookingData(){
    fetch(bookingAPI)
    .then(res => res.json())
    .then(data => data.data)
    .then(bookings => {
        bookings.forEach(booking => {
            //行程確認form
            const itineraryForm = document.createElement('form')
            itineraryForm.classList.add('itinerary')
            
            //景點照片
            const attrIMG = document.createElement('img')
            attrIMG.src = booking.attraction.image
            
            //包行程資訊
            const attrInfo = document.createElement('div')
            attrInfo.classList.add('info')
            
            //景點名稱
            const attrName = document.createElement('h4')
            attrName.innerText = `台北一日遊：${booking.attraction.name}`

            //刪除按鈕
            const deleteButton = document.createElement('button')
            const icon = document.createElement('i')
            icon.classList.add('fas', 'fa-trash-alt')
            deleteButton.append(icon)

            //包date
            const dateContain = document.createElement('div')
            
        })
    })
}
