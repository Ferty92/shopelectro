(() => {
  const DOM = {
    $copyPhoneTag: $('.js-copy-phone'),
    $copyEmailTag: $('.js-copy-mail'),
    $backcallModal: $('.js-backcall-order'),
    $searchForm: $('.js-search-form'),
    $btnToCartProductPage: $('.js-to-cart-on-product-page'),
    $btnToCartCategoryPage: $('.js-product-to-cart'),
    $cartHeader: $('.js-cart-header'),
    goToCartLink: '.js-go-to-cart',
    $removeFromCart: $('.js-remove'),
    $goToProductLink: $('.js-browse-product'),
    $downloadPrice: $('.js-download-price'),
    $downloadPriceInFooter: $('.js-download-price-footer'),
  };

  const config = {
    phoneRegexp: /\d{3}-\d{2}-\d{2}/g,
    fullEmail: 'info@shopelectro.ru',
  };

  const init = () => {
    setUpListeners();
  };

  function setUpListeners() {
    mediator.subscribe('onOneClickBuy', () => {
      reachGoal('CMN_BUY_SEND');
      reachGoal('FAST_BUY_SEND');
    });
    mediator.subscribe('onOrderSend', () => {
      reachGoal('CMN_BUY_SEND');
      reachGoal('FULL_BUY_SEND');
    });
    mediator.subscribe('onProductRemove', () => reachGoal('DELETE_PRODUCT'));
    mediator.subscribe('onBackCallSend', () => reachGoal('BACK_CALL_SEND'));

    DOM.$searchForm.submit(() => reachGoal('USE_SEARCH_FORM'));
    DOM.$removeFromCart.click(() => reachGoal('DELETE_PRODUCT'));
    DOM.$cartHeader.on('click', DOM.goToCartLink, () => reachGoal('CART_OPEN'));
    DOM.$backcallModal.click(() => reachGoal('BACK_CALL_OPEN'));
    DOM.$goToProductLink.click(() => reachGoal('PROD_BROWSE'));
    DOM.$downloadPrice.click(() => reachGoal('PRICE_HEADER'));
    DOM.$downloadPriceInFooter.click(() => reachGoal('PRICE_FOOTER'));
    DOM.$btnToCartProductPage
      .click(() => {
        reachGoal('PUT_IN_CART_FROM_PRODUCT');
        reachGoal('CMN_PUT_IN_CART');
      });
    DOM.$btnToCartCategoryPage
      .click(() => {
        reachGoal('PUT_IN_CART_FROM_CATEGORY');
        reachGoal('CMN_PUT_IN_CART');
      });
    DOM.$copyPhoneTag.mouseup(reachCopyPhone);
    DOM.$copyEmailTag.mouseup(reachCopyEmail);
  }

  function reachGoal(goal) {
    yaCounter20644114.reachGoal(goal);
  }

  /**
   * Returns copied text by user.
   * http://stackoverflow.com/questions/5379120/get-the-highlighted-selected-text
   */
  const getSelectionText = () => window.getSelection().toString();

  /**
   * Fire when user selects 9 or more numbers of phone.
   */
  function reachCopyPhone() {
    const selectedTextLength = getSelectionText().length;

    if (selectedTextLength > 8) {
      localStorage.setItem('phoneIsCopied', 'true');
      reachGoal('COPY_PHONE');
    }
  }

  /**
   * We store this users event for current user.
   * So it fires once per user.
   */
  const isFullMailCopied = () => getSelectionText().indexOf(config.fullEmail) === 0;

  function reachCopyEmail() {
    const wasEmailCopied = localStorage.getItem('mailIsCopied');

    if (isFullMailCopied && !wasEmailCopied) {
      localStorage.setItem('mailIsCopied', 'true');
      reachGoal('COPY_MAIL');
    }
  }

  init();
})();
