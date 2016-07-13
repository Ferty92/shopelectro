const order = (() => {
  const DOM = {
    $fancybox: $('.fancybox'),
    $formErrorText: $('.js-form-error-text'),
    $order: $('.js-order-contain'),
    yandexSubmit: '#btn-send-ya',
    seSubmit: '#btn-send-se',
    yandexForm: '#yandex-form',
    productCount: '.js-prod-count',
    remove: '.js-remove',
    paymentOptions: 'input[name=payment_option]',
    orderForm: {
      name: '#id_name',
      phone: '#id_phone',
      email: '#id_email',
      city: '#id_city',
    },
    yandexOrderInfo: {
      customer: 'input[name=customerNumber]',
      order: 'input[name=orderNumber]',
      payment: 'input[name=paymentType]',
    },
  };

  // TODO: maybe we should move all the configs into separate file.
  // http://youtrack.stkmail.ru/issue/dev-748
  const CONFIG = {
    touchspin: {
      min: 1,
      max: 10000,
      verticalbuttons: true,
      verticalupclass: 'glyphicon glyphicon-plus',
      verticaldownclass: 'glyphicon glyphicon-minus',
    },
    citiesAutocomplete: {
      types: ['(cities)'],
      componentRestrictions: {
        country: 'ru',
      },
    },
    sePayments: ['cash', 'cashless'],
    paymentKey: 'payment',
  };

  const init = () => {
    pluginsInit();
    setUpListeners();
    fillSavedInputs();
    restoreSelectedPayment();
    selectPaymentSubmit();
  };

  const pluginsInit = () => {
    googleAutocomplete();
  };

  const setUpListeners = () => {
    $(DOM.yandexForm).submit(() => mediator.publish('onOrderSend'));

    /**
     * Bind events to parent's elements, because we can't bind event to dynamically added element.
     * @param eventName - standard event name
     * @param element - element, which is a child of parent's element (DOM.$order)
     * @param handler - callable which will be dispatched on event
     */
    const subscribeOrderEvent = (eventName, element, handler) => {
      DOM.$order.on(eventName, element, handler);
    };
    const getEventTarget = event => $(event.target);

    subscribeOrderEvent('change', DOM.productCount, event => changeProductCount(event));
    subscribeOrderEvent('click', DOM.remove, event => {
      remove(event.target.getAttribute('productId'));
    });
    subscribeOrderEvent('keyup', 'input', event => storeInput(getEventTarget(event)));
    subscribeOrderEvent('click', DOM.paymentOptions, event => {
      selectPaymentSubmit(event.target.getAttribute('value'));
    });
    subscribeOrderEvent('click', DOM.yandexSubmit, submitYandexOrder);

    mediator.subscribe('onCartUpdate', renderTable, touchSpinReInit);
  };

  /**
   * Init google cities autocomplete.
   */
  const googleAutocomplete = () => {
    const cityField = document.getElementById('id_city');
    if (!cityField) return;

    const citiesAutocomplete = new google.maps.places.Autocomplete(
      cityField, CONFIG.citiesAutocomplete);

    google.maps.event.addListener(citiesAutocomplete, 'place_changed', () => {
      storeInput($(DOM.orderForm.city));
    });
  };

  /**
   * Fill inputs, which have saved to localstorage value.
   * Runs on page load, and on every cart's update.
   */
  const touchSpinReInit = () => {
    $(DOM.productCount).TouchSpin(CONFIG.touchspin);
  };

  /**
   * Fill inputs, which have saved to localstorage value.
   * Runs on page load, and on every cart's update.
   */
  const fillSavedInputs = () => {
    const getFieldByName = (name) => $(`#id_${name}`);

    for (const fieldName in DOM.orderForm) {
      if ({}.hasOwnProperty.call(DOM.orderForm, fieldName)) {
        const $field = getFieldByName(fieldName);
        const savedValue = localStorage.getItem(fieldName);

        if ($field && savedValue) {
          $field.val(savedValue);
        }
      }
    }
  };

  /**
   * Select saved payment if there is one.
   */
  const restoreSelectedPayment = () => {
    const savedPayment = localStorage.getItem(CONFIG.paymentKey);

    if (savedPayment) {
      const isSelected = $option => $option.val() === savedPayment;

      $(DOM.paymentOptions).each((_, el) => {
        const $inputOption = $(el);
        $inputOption.attr('checked', isSelected($inputOption));
      });
    }
  };

  /**
   * Event handler for changing product's count in Cart.
   * We wait at least 100ms every time the user pressed the button.
   */
  const changeProductCount = (event) => {
    const productID = event.target.getAttribute('productId');
    const newCount = event.target.value;

    setTimeout(
      () => server.changeInCart(productID, newCount)
        .then(data => mediator.publish('onCartUpdate', data)), 100
    );
  };

  /**
   * Return name (which is value) of a selected payment option.
   */
  const getSelectedPaymentName = () => {
    const $selectedOption = $(DOM.paymentOptions + ':checked');
    return $selectedOption.val();
  };

  /**
   * Select appropriate submit button, based on selected payment option.
   */
  const selectPaymentSubmit = () => {
    const $yandexSubmit = $(DOM.yandexSubmit);
    const $seSubmit = $(DOM.seSubmit);
    const optionName = getSelectedPaymentName();
    const isYandexPayment = CONFIG.sePayments.indexOf(optionName) === -1;

    const selectSE = () => {
      $yandexSubmit.addClass('hidden');
      $seSubmit.removeClass('hidden');
    };

    const selectYandex = () => {
      $seSubmit.addClass('hidden');
      $yandexSubmit.removeClass('hidden');
    };

    isYandexPayment ? selectYandex() : selectSE();
    localStorage.setItem(CONFIG.paymentKey, optionName);
  };

  /**
   * Return hash with customer's info from form.
   */
  const getCustomerInfo = () => {
    const customerInfo = {};

    $.each(DOM.orderForm, (name, field) => {
      customerInfo[name] = $(field).val();
    });

    return customerInfo;
  };

  /**
   * Submit Yandex order if user's phone is provided.
   * It consists of several steps:
   *
   * 1. Get customerNumber (which is a phone without any non-numeric chars)
   * 2. Hit backend and save Order to DB. This step returns id of an order.
   * 3. Fill Yandex-form
   * 4. Submit Yandex-form.
   */
  const submitYandexOrder = event => {
    event.preventDefault();

    const getCustomerNumber = phone => phone.replace(/\D/g, '');
    const fillYandexForm = orderId => {
      $(DOM.yandexOrderInfo.order).val(orderId);
      $(DOM.yandexOrderInfo.customer).val(getCustomerNumber(customerInfo.phone));
      $(DOM.yandexOrderInfo.payment).val(getSelectedPaymentName());
    };

    const customerInfo = getCustomerInfo();

    // TODO: Form phone & mail validation need to be realize.
    // Fields should have required attr. The code locates in rf-components.
    if (!validator.isPhoneValid(customerInfo.phone)) {
      DOM.$formErrorText.removeClass('hidden').addClass('shake animated');
      return;
    }

    server.sendYandexOrder(customerInfo)
      .then(id => {
        fillYandexForm(id);
        $(DOM.yandexForm).submit();
      });
  };

  /**
   * Store inputted value into LocalStorage.
   */
  const storeInput = target => {
    localStorage.setItem(target.attr('name'), target.val());
  };

  /**
   * Remove product from cart's table and dispatches 'onCartUpdate' event.
   */
  const remove = productId => {
    server.removeFromCart(productId).then(data => {
      mediator.publish('onCartUpdate', data);
    });
  };

  /**
   * Render table and form.
   * After that, fill in saved form data.
   */
  const renderTable = (event, data) => {
    DOM.$order.html(data.table);
    fillSavedInputs();
    restoreSelectedPayment();
    selectPaymentSubmit();
  };

  init();
})();
