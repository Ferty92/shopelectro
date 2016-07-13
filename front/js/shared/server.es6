const server = (() => {
  const CONFIG = {
    orderCallUrl: '/shop/order-call/',
    addToCartUrl: '/shop/cart-add/',
    oneClickBuyUrl: '/shop/one-click-buy/',
    changeCartUrl: '/shop/cart-change/',
    removeFromCartUrl: '/shop/cart-remove/',
    flushCartUrl: '/shop/cart-flush/',
    yandexOrderUrl: '/shop/yandex-order/',
    setViewTypeUrl: '/set-view-type/',
  };

  /**
   * Send information about order call.
   * @param phone
   * @param time
   * @param url
   */
  const sendOrderCall = (phone, time, url) => $.post(CONFIG.orderCallUrl, { phone, time, url });

  /**
   * @param url
   */
  const fetchProducts = url => fetch(url).then(response => response.text());

  /**
   * Send viewType to store user's default view type.
   * @param event
   * @param viewType
   */
  const sendViewType = (event, viewType) => $.post(CONFIG.setViewTypeUrl, { view_type: viewType });

  /**
   * Add product to backend's Cart.
   * @param productId
   * @param quantity
   */
  const addToCart = (productId, quantity) => {
    return $.post(
      CONFIG.addToCartUrl,
      {
        product: productId,
        quantity,
      }
    );
  };

  /**
   * Flush (clear) the cart on backend.
   */
  const flushCart = () => $.post(CONFIG.flushCartUrl);

  /**
   * Handle one-click-buy feature. Sends:
   * @param product  - id of a bought product
   * @param quantity - selected quantity
   * @param phone    - customer's phone
   */
  const oneClickBuy = (product, quantity, phone) => {
    return $.post(CONFIG.oneClickBuyUrl, { product, quantity, phone });
  };

  /**
   * Remove given product from Cart.
   * @param productId
   */
  const removeFromCart = productId => $.post(CONFIG.removeFromCartUrl, { product: productId });

  /**
   * Return $.post request, which changes quantity of a given Product in Cart.
   * @param productId
   * @param quantity - new quantity of a product
   */
  const changeInCart = (productId, quantity) => {
    return $.post(
      CONFIG.changeCartUrl,
      {
        product: productId,
        quantity,
      }
    );
  };

  const sendYandexOrder = data => $.post(CONFIG.yandexOrderUrl, data);

  return {
    sendOrderCall,
    fetchProducts,
    sendViewType,
    addToCart,
    flushCart,
    oneClickBuy,
    removeFromCart,
    changeInCart,
    sendYandexOrder,
  };
})();
