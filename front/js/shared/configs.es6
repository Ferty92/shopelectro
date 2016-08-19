/**
 * There are all common configs for all common plugins.
 * This module is an entry point for plugins initialization.
 */
const configs = (() => {
  const DOM = {
    scrollWrapper: '#scroll-wrapper',
    $touchspin: $('.js-touchspin'),
    $phoneInputs: $('.js-masked-phone'),
  };

  const labels = {
    callTime: 'callTime',
    phone: 'phone',
  };

  const plugins = {
    scrollbar: {
      autoReinitialise: true,
      mouseWheelSpeed: 30,
    },
    touchspin: {
      min: 1,
      max: 10000,
      verticalbuttons: true,
      verticalupclass: 'glyphicon glyphicon-plus',
      verticaldownclass: 'glyphicon glyphicon-minus',
    },
    fancybox: {
      openEffect: 'fade',
      closeEffect: 'elastic',
      helpers: {
        overlay: {
          locked: false,
        },
      },
    },
  };

  const init = () => {
    pluginsInit();
    setupXHR();
  };

  /**
  * Set all unsafe ajax requests with csrftoken.
  */
  const setupXHR = () => {
    const csrfUnsafeMethod = method => !(/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));

    $.ajaxSetup({
      beforeSend: (xhr, settings) => {
        if (csrfUnsafeMethod(settings.type)) {
          xhr.setRequestHeader('X-CSRFToken', Cookies.get('csrftoken'));
        }
      },
    });
  };

  const pluginsInit = () => {
    $(DOM.scrollWrapper).jScrollPane(plugins.scrollbar);
    DOM.$touchspin.TouchSpin(plugins.touchspin);

    DOM.$phoneInputs
      .mask('+0 (000) 000 00 00', {
        placeholder: '+7 (999) 000 00 00',
      })
      .on('keyup', (event) => {
        localStorage.setItem(labels.phone, $(event.target).val());
      });
  };

  const scrollbarReinit = () => $(DOM.scrollWrapper).jScrollPane(plugins.scrollbar);

  init();

  return { plugins, setupXHR, labels, scrollbarReinit };
})();