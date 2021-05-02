const ccn = document.querySelector('#ccn'),
      cce = document.querySelector('#cce'),
      cvv = document.querySelector('#cvv')

// Payment.restrictNumeric(numeric);
Payment.formatCardNumber(ccn, 16);
Payment.formatCardExpiry(cce);
Payment.formatCardCVC(cvv);