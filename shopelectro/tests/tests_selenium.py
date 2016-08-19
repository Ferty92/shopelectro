"""
Selenium-based tests.

If you need to create new test-suite, subclass it from SeleniumTestCase class.
Every Selenium-based test suite uses fixture called dump.json.
"""

import time

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from seleniumrequests import Chrome  # We use this instead of standard selenium

from django.conf import settings
from django.test import LiveServerTestCase
from django.test.utils import override_settings
from django.core.urlresolvers import reverse

from pages.models import Page


def wait(seconds=1):
    """Simple wrapper on time.sleep() method."""
    time.sleep(seconds)


def hover(browser, element):
    """Perform a hover over an element."""
    ActionChains(browser).move_to_element(element).perform()


def context_click(browser, element):
    ActionChains(browser).context_click(element).perform()
    wait()


class SeleniumTestCase(LiveServerTestCase):
    """Common superclass for running selenium-based tests."""

    fixtures = ['dump.json']

    @classmethod
    def setUpClass(cls):
        """Instantiate browser instance."""
        super(SeleniumTestCase, cls).setUpClass()
        cls.browser = Chrome()
        cls.browser.implicitly_wait(5)
        cls.browser.maximize_window()

    @classmethod
    def tearDownClass(cls):
        """Closes selenium's session."""
        cls.browser.quit()
        super(SeleniumTestCase, cls).tearDownClass()


class Header(SeleniumTestCase):
    """Selenium-based tests for header."""

    def setUp(self):
        """Sets up testing urls and dispatches selenium webdriver."""
        self.browser.get(self.live_server_url)

    @property
    def call_button(self):
        return self.browser.find_element_by_class_name('feedback-but-btn')

    def test_call_modal_not_visible(self):
        """By default we shouldn't see call modal."""
        modal = self.browser.find_element_by_id('back-call-modal')
        self.assertFalse(modal.is_displayed())

    def test_call_modal_after_click_call_button(self):
        """After clicking on call button we should see call modal."""
        self.call_button.click()
        wait()
        modal = self.browser.find_element_by_id('back-call-modal')
        self.assertTrue(modal.is_displayed())

    def test_order_call(self):
        """After filling modal's fields we can successfully order call."""
        self.call_button.click()
        wait()
        self.browser.find_element_by_id(
            'back-call-phone').send_keys('22222222222')
        self.browser.find_element_by_xpath(
            '//*[@id="back-call-time"]/option[3]').click()
        self.browser.find_element_by_class_name('js-send-backcall').click()
        wait()
        self.assertTrue(self.browser.find_element_by_class_name(
            'js-backcall-success').is_displayed())

    def test_empty_cart(self):
        """By default there should be 'Корзина пуста' in the header's cart."""
        cart_in_header = self.browser.find_element_by_class_name(
            'js-header-cart')
        self.assertTrue('Корзина пуста' in cart_in_header.text)

    def test_cart_hover(self):
        """When hover, cart dropdown should be visible."""
        cart_parent = self.browser.find_element_by_class_name('basket-parent')
        hover(self.browser, cart_parent)
        cart = self.browser.find_element_by_class_name('basket-wrapper')
        self.assertTrue(cart.is_displayed())

    def test_cart_flush(self):
        """We can flush cart from header's cart dropdown"""
        self.browser.get(self.live_server_url + reverse('product', args=(250,)))
        self.browser.find_element_by_class_name('btn-to-basket').click()
        wait()
        cart_parent = self.browser.find_element_by_class_name('basket-parent')
        hover(self.browser, cart_parent)
        self.browser.find_element_by_class_name('basket-reset').click()
        wait()
        cart_is_empty = self.browser.find_element_by_class_name('js-cart-is-empty')
        self.assertTrue(cart_is_empty.is_displayed())


class CategoryPage(SeleniumTestCase):
    """Selenium-based tests for Category Page."""

    @classmethod
    def setUpClass(cls):
        """Sets up testing urls."""
        super(CategoryPage, cls).setUpClass()
        server = cls.live_server_url
        testing_url = lambda slug: server + reverse('category', args=(slug,))
        cls.direct_child = testing_url('child-1-of-root-category-1')
        cls.deep_category = testing_url('child-2-of-child-2-of-root-category-1')
        cls.root_category = testing_url('root-category-1')

    @property
    def load_more_button(self):
        return self.browser.find_element_by_id('btn-load-products')

    def test_breadcrumbs(self):
        """
        Breadcrumbs should be presented on every category page.
        Their count depends on category's depth in a catalog tree.
        For the root categories, for example, there should be 3 crumbs.
        :return:
        """

        # In 'root category' there should be three crumbs
        self.browser.get(self.root_category)
        crumbs = self.browser.find_elements_by_class_name('breadcrumbs-item')
        self.assertEqual(len(crumbs), 3)

        # In 'deep category' there should be more crumbs
        self.browser.get(self.deep_category)
        crumbs = self.browser.find_elements_by_class_name('breadcrumbs-item')
        self.assertEqual(len(crumbs), 5)

    def test_30_products_by_default(self):
        """By default any CategoryPage should contain 30 products."""

        self.browser.get(self.root_category)
        loaded_products = self.browser.find_element_by_class_name(
            'js-products-showed-count').text
        self.assertEqual('30', loaded_products)

    def test_load_more_products(self):
        """
        We can load another 30 by clicking load more button.

        After that we wait some time for XHR will be performed
        and there will be new count of loaded products.
        """

        self.browser.get(self.root_category)
        self.browser.refresh()
        self.load_more_button.click()  # Let's load another 30 products.
        wait()
        loaded_products_count = self.browser.find_element_by_class_name(
            'js-products-showed-count').text
        self.assertEqual('60', loaded_products_count)

    def test_load_more_hidden_in_fully_loaded_categories(self):
        """
        If category has less products than LOAD_LIMIT
        we shouldn't see load more button.
        """

        self.browser.get(self.deep_category)
        self.assertTrue('hidden' in self.load_more_button.get_attribute('class'))

    def test_default_view_is_tile(self):
        """
        By default, category page should has tile view

        It means, after rendering a page,
        tile view selector should has 'active' class
        and category wrapper 'view-mode-tile' class.
        """

        self.browser.get(self.direct_child)
        tile_view_selector = self.browser.find_element_by_class_name(
            'js-icon-mode-tile')
        products_view = self.browser.find_element_by_id('category-right')
        self.assertTrue('active' in tile_view_selector.get_attribute('class'))
        self.assertTrue('view-mode-tile' in products_view.get_attribute('class'))

    def test_change_view(self):
        """
        We should be able to change default view
        to list view without reloading a page.
        """

        self.browser.get(self.direct_child)
        list_view_selector = self.browser.find_element_by_class_name(
            'js-icon-mode-list')
        products_view = self.browser.find_element_by_id('category-right')

        self.assertFalse('active' in
                         list_view_selector.get_attribute('class'))
        self.assertFalse('view-mode-list' in
                         products_view.get_attribute('class'))

        list_view_selector.click()
        self.assertTrue('active' in
                        list_view_selector.get_attribute('class'))
        self.assertTrue('view-mode-list' in
                        products_view.get_attribute('class'))

    def test_default_sorting_is_by_cheapest(self):
        """By default, sorting should be by cheapest goods."""

        self.browser.get(self.direct_child)
        cheapest_sort_option = self.browser.find_element_by_xpath(
            '//*[@id="category-right"]/'
            'div[1]/div/div/div[2]/label/div/select/option[1]')
        self.assertTrue(cheapest_sort_option.is_selected())

    def test_change_sorting(self):
        """We can change sorting option"""

        self.browser.get(self.direct_child)
        expensive_sort_option = self.browser.find_element_by_xpath(
            '//*[@id="category-right"]/'
            'div[1]/div/div/div[2]/label/div/select/option[3]'
        )
        expensive_sort_option.click()
        expensive_sort_option = self.browser.find_element_by_xpath(
            '//*[@id="category-right"]/'
            'div[1]/div/div/div[2]/label/div/select/option[3]'
        )
        self.assertTrue(expensive_sort_option.is_selected())

    def test_add_to_cart(self):
        """We can add item to cart from it's category page."""

        self.browser.get(self.direct_child)
        self.browser.find_elements_by_class_name(
            'js-product-to-cart')[0].click()
        wait()
        cart_is_empty = self.browser.find_element_by_class_name(
            'js-cart-is-empty')
        self.assertFalse(cart_is_empty.is_displayed())


class ProductPage(SeleniumTestCase):
    """Selenium-based tests for product page UI."""

    PRODUCT_ID = 280

    def setUp(self):
        """Sets up testing url and dispatches selenium webdriver."""

        server = self.live_server_url

        self.test_product_page = server + reverse(
            'product', args=(self.PRODUCT_ID,))
        self.success_order = server + reverse('ecommerce:order_success')
        self.product_name = 'Product of Child #1 of #Root category #0 with num #7'
        self.browser.get(self.test_product_page)
        self.one_click = self.browser.find_element_by_id('btn-one-click-order')

    def test_breadcrumbs(self):
        """
        Breadcrumbs should be presented on every product page.
        Their count depends on product's depth in a catalog tree.
        :return:
        """

        # There should be 5 items in breadcrumbs for this case
        crumbs = self.browser.find_elements_by_class_name('breadcrumbs-item')
        self.assertEqual(len(crumbs), 5)

    def test_ui_elements(self):
        """
        Every ProductPage should have buttons to make order and input
        for phone number
        """

        button_order = self.browser.find_element_by_id('btn-to-basket')
        input_one_click_order = self.browser.find_element_by_id(
            'input-one-click-phone')
        self.assertTrue(button_order)
        self.assertTrue(self.one_click)
        self.assertTrue(input_one_click_order)

    def test_fancybox(self):
        """ProductPage should have fancyBox plugin"""

        self.browser.find_element_by_id('product-image-big').click()
        wait()
        fancybox_wrap = self.browser.find_element_by_class_name('fancybox-wrap')

        self.assertTrue(fancybox_wrap)

    def test_images_switch(self):
        """If product has > 1 image, we could to switch them by clicking."""

        product_main_img = self.browser.find_element_by_id('product-image-big')
        wait()
        self.assertTrue('main' in product_main_img.get_attribute('src'))

        self.browser.find_element_by_xpath('//*[@id="product-images"]/div[3]/img').click()
        wait()

        product_main_img = self.browser.find_element_by_id('product-image-big')
        self.assertFalse('main' in product_main_img.get_attribute('src'))

    def test_one_click_buy_disabled_with_empty_phone(self):
        """By default .btn-one-click-order should be disabled"""

        self.browser.find_element_by_id(
            'input-one-click-phone').send_keys(Keys.BACKSPACE)
        self.assertTrue(self.one_click.get_attribute('disabled'))

    def test_one_click_buy_action(self):
        """We can order product via one-click buy button."""

        self.browser.find_element_by_id(
            'input-one-click-phone').send_keys('22222222222')
        self.one_click.click()
        wait()
        self.assertEqual(self.browser.current_url, self.success_order)

    def test_add_to_cart(self):
        """We can add item to cart from it's page."""

        self.browser.find_element_by_class_name('btn-to-basket').click()
        wait()
        cart_is_empty = self.browser.find_element_by_class_name('js-cart-is-empty')
        self.assertFalse(cart_is_empty.is_displayed())

    def test_product_name_in_cart_dropdown(self):
        self.browser.find_element_by_class_name('btn-to-basket').click()
        wait()
        cart_parent = self.browser.find_element_by_class_name('basket-parent')
        hover(self.browser, cart_parent)
        cart = cart_parent.find_element_by_class_name('basket-wrapper')
        self.assertTrue(self.product_name in cart.text)

    def test_actual_product_count_in_cart_dropdown(self):
        self.browser.find_element_by_id('product-count').send_keys('42')
        self.browser.find_element_by_class_name('btn-to-basket').click()
        wait()
        cart_parent = self.browser.find_element_by_class_name('basket-parent')
        hover(self.browser, cart_parent)
        cart_size = self.browser.find_element_by_class_name('js-cart-size')
        self.assertTrue('42' in cart_size.text)


class OrderPage(SeleniumTestCase):

    @staticmethod
    def get_cell(pos, col):
        # table columns mapping:  http://prntscr.com/bsv5hp
        COLS = {
            'id': 1,
            'name': 3,
            'count': 4,
            'price': 5,
            'remove': 6,
        }
        product_row = \
            '//*[@id="js-order-list"]/tbody/tr[{pos}]/td[{col}]'

        return product_row.format(pos=pos, col=COLS[col])


    @classmethod
    def setUpClass(cls):
        super(OrderPage, cls).setUpClass()
        cls.category = reverse('category', args=(
            'child-1-of-root-category-1',))
        cls.cart_dropdown = 'basket-parent'
        cls.first_product_id = '405'
        cls.remove_product = cls.get_cell(pos=4, col='remove') + '/img'
        cls.product_count = cls.get_cell(pos=4, col='count') + '/div[2]/input'
        cls.add_product = \
            cls.get_cell(pos=4, col='count') + '/div[2]/span[3]/button[1]'

    def setUp(self):
        self.__buy_products()
        wait()
        self.browser.get(self.live_server_url +
                         reverse('ecommerce:order_page'))

    def __buy_products(self):
        self.browser.get(self.live_server_url + self.category)
        for i in range(1, 6):
            self.browser.find_element_by_xpath(
                '//*[@id="products-wrapper"]/div[{}]/div[2]/div[5]/button'
                    .format(i)
            ).click()

    def test_table_is_presented_if_there_is_some_products(self):
        """
        If there are some products in cart,
        we should see them in table on OrderPage.
        """

        order_table = self.browser.find_element_by_class_name('order-list')
        self.assertTrue(order_table.is_displayed())

    def test_remove_product_from_table(self):
        """We can remove product from table and see the changes immediately."""
        first_row_remove = self.browser.find_element_by_xpath(
            self.remove_product)
        first_row_remove.click()
        wait()
        self.assertFalse(
            self.first_product_id in
            self.browser.find_element_by_class_name('order-list').text)

    def test_empty_cart(self):
        """
        After removing every product from cart
        we should see that it is empty.
        """

        removes = self.browser.find_elements_by_class_name('js-remove')
        while removes:
            remove = removes[0]
            remove.click()
            wait()
            removes = self.browser.find_elements_by_class_name('js-remove')

        self.assertTrue('Корзина пуста' in
                        self.browser.find_element_by_class_name(
                            'js-order-contain').text)

    def test_table_and_dropdown_are_synchronized(self):
        def get_counts():
            table_count = (self.browser
                           .find_element_by_id('cart-page-prods-count')
                           .text)
            header_count = (self.browser
                            .find_element_by_class_name('js-cart-size')
                            .text)
            return table_count, header_count

        self.browser.refresh()
        table_count, dropdown_count = get_counts()
        self.assertEqual(table_count, '5')
        self.assertEqual(dropdown_count, table_count)
        self.browser.find_element_by_xpath(
            self.add_product.format(self.first_product_id)).click()
        wait()

        table_count, dropdown_count = get_counts()
        self.assertEqual(table_count, '6')
        self.assertEqual(table_count, dropdown_count)
        wait()

        self.browser.find_element_by_xpath(
            self.remove_product.format(self.first_product_id)).click()
        wait()

        table_count, dropdown_count = get_counts()
        self.assertEqual(table_count, dropdown_count)
        self.assertEqual(table_count, '4')

    def test_confirm_order(self):
        """After filling the form we should be able to confirm an order."""

        self.browser.find_element_by_id('id_payment_option_0').click()
        add_one_more = self.browser.find_element_by_xpath(self.add_product)
        add_one_more.click()  # perform some operations on cart
        wait()
        self.fill_and_submit_form()
        wait()
        self.assertEqual(self.browser.current_url,
                         self.live_server_url +
                         reverse('ecommerce:order_success'))

    def fill_and_submit_form(self, yandex=False):
        self.browser.find_element_by_id('id_name').send_keys('Name')
        self.browser.find_element_by_id('id_city').send_keys('Санкт-Петербург')
        self.browser.find_element_by_id('id_phone').send_keys('22222222222')
        self.browser.find_element_by_id('id_email').send_keys('test@test.test')
        wait()
        submit = 'btn-send-ya' if yandex else 'btn-send-se'
        self.browser.find_element_by_id(submit).click()

    def test_yandex_order_without_phone(self):
        """
        We should see error text message when trying to
        submit form without phone number.
        """

        self.browser.find_element_by_id('id_payment_option_2').click()
        self.browser.find_element_by_id('id_name').send_keys('Name')
        self.browser.find_element_by_id('id_phone').clear()
        self.browser.find_element_by_id('btn-send-ya').click()
        error_text = self.browser.find_element_by_class_name(
            'js-form-error-text')
        self.assertTrue('телефон', error_text.is_displayed())


class SitePage(SeleniumTestCase):

    def setUp(self):
        self.page_top = Page.objects.create(
            title='Navigation',
            slug='navi',
            type=Page.FLAT_TYPE
        )
        self.page_last = Page.objects.create(
            title='Contacts',
            slug='contacts',
            type=Page.FLAT_TYPE,
            parent=self.page_top
        )
        self.browser.get(self.live_server_url + self.page_last.get_absolute_url())
        self.browser.execute_script('localStorage.clear();')
        self.browser.get(self.live_server_url + self.page_last.get_absolute_url())
        wait()

    @property
    def accordion_title(self):
        return self.browser.find_element_by_id(
            'js-accordion-title-{}'.format(self.page_top.id))

    @property
    def accordion_content(self):
        return self.browser.find_element_by_id(
            'js-accordion-content-{}'.format(self.page_top.id))

    def test_accordion_minimized(self):
        """Accordion item should be minimized by default"""

        self.assertFalse(self.accordion_content.is_displayed())

    def test_accordion_expand(self):
        """Accordion item should expand by click on title"""
        accordion_title = self.accordion_title
        accordion_content = self.accordion_content
        accordion_title.click()
        wait()
        self.assertTrue(accordion_content.is_displayed())

    def test_accordion_minimize_by_double_click(self):
        """Accordion item should be minimized by two clicks on title"""
        accordion_title = self.accordion_title
        accordion_content = self.accordion_content
        accordion_title.click()
        wait()
        accordion_title.click()
        wait()
        self.assertFalse(accordion_content.is_displayed())


class AdminPage(SeleniumTestCase):
    """Selenium-based tests for Admin page UI."""

    fixtures = ['dump.json', 'admin.json']

    @classmethod
    def setUpClass(cls):
        super(AdminPage, cls).setUpClass()
        cls.admin_page = cls.live_server_url + reverse('admin:index')
        cls.login = 'admin'
        cls.password = 'asdfjkl;'
        cls.title_text = 'Shopelectro administration'
        cls.products = 'admin-products-link'
        cls.price_filter = '//*[@id="changelist-filter"]/ul[1]/li[3]'
        cls.active_products = '//*[@id="changelist-filter"]/ul[2]/li[2]/a'
        cls.inactive_products = '//*[@id="changelist-filter"]/ul[2]/li[3]/a'
        cls.is_active_img = 'field-is_active'
        cls.autocomplete_text = 'Prod'
        cls.tree_root_node_id = '24'
        cls.tree_node_id = '28'

    def setUp(self):
        """Sets up testing url and dispatches selenium webdriver."""

        self.browser.get(self.admin_page)
        login_field = self.browser.find_element_by_id('id_username')
        login_field.clear()
        login_field.send_keys(self.login)
        password_field = self.browser.find_element_by_id('id_password')
        password_field.clear()
        password_field.send_keys(self.password)
        login_form = self.browser.find_element_by_id('login-form')
        login_form.submit()
        wait()

    def test_login(self):
        """We are able to login to Admin page."""

        admin_title = self.browser.find_element_by_id('site-name')
        self.assertIn(self.title_text, admin_title.text)

    def test_admin_product(self):
        """
        Admin products page has icon links for Edit.
        And it should has Search field.
        """

        self.browser.find_element_by_id(self.products).click()
        edit_link = self.browser.find_element_by_class_name('field-links')

        self.assertTrue(edit_link)

    def test_product_price_filter(self):
        """
        Price filter is able to filter products by set range.
        In this case we filter products with 1000 - 2000 price range.
        """

        self.browser.find_element_by_id(self.products).click()
        self.browser.find_element_by_xpath(self.price_filter).click()
        wait(2)
        product = self.browser.find_element_by_xpath('//*[@id="result_list"]/tbody/tr[1]/td[3]')
        product_price = float(product.text)

        self.assertTrue(product_price >= 1000)

    def test_is_active_filter(self):
        """Activity filter returns only active or non active items."""

        self.browser.find_element_by_id(self.products).click()
        wait()

        self.browser.find_element_by_xpath(self.active_products).click()
        wait()

        first_product = self.browser.find_element_by_class_name(
            self.is_active_img).find_element_by_tag_name('img')
        first_product_state = first_product.get_attribute('alt')

        self.assertTrue(first_product_state == 'true')

        self.browser.find_element_by_xpath(self.inactive_products).click()
        wait()
        results = self.browser.find_element_by_class_name('paginator')

        self.assertTrue('0' in results.text)

    def test_search_autocomplete(self):
        """Search field could autocomplete."""

        self.browser.find_element_by_id(self.products).click()
        wait()

        self.browser.find_element_by_id('searchbar').send_keys(self.autocomplete_text)
        wait()

        first_suggested_item = self.browser.find_element_by_class_name(
            'autocomplete-suggestion')
        first_suggested_item_text = first_suggested_item.get_attribute(
            'data-val')

        self.assertTrue(self.autocomplete_text in first_suggested_item_text)

    def test_sidebar_not_on_dashboard(self):
        """Sidebar should be not only on dashboard page."""

        self.browser.find_element_by_id(self.products).click()
        wait()
        sidebar = self.browser.find_element_by_class_name('sidebar')

        self.assertTrue(sidebar.is_displayed())

    def test_tree_fetch_data(self):
        """Test for lazy load logic"""
        # open root node
        self.browser.find_element_by_id(self.tree_root_node_id).find_element_by_tag_name('i').click()
        wait()
        # open child node
        self.browser.find_element_by_id(self.tree_node_id).find_element_by_tag_name('i').click()
        wait()

        node_children = self.browser.find_element_by_id(self.tree_node_id).find_elements_by_class_name('jstree-leaf')

        self.assertGreater(len(node_children), 10)

    def test_tree_redirect_to_entity_edit_page(self):
        """Test redirect to edit entity page by click at tree's item"""
        h1 = 'Change category'

        # click at tree's item, redirect to entity edit page
        self.browser.find_element_by_id(self.tree_root_node_id).find_element_by_tag_name('a').click()
        test_h1 = self.browser.find_elements_by_tag_name('h1')[1].text

        self.assertEqual(h1, test_h1)

    def test_tree_redirect_to_table_editor_page(self):
        """Test redirect to table editor page by context click at tree's item"""
        tree_item = self.browser.find_element_by_id(self.tree_node_id).find_element_by_tag_name('a')
        search_value = 'Child #0 of #Root category #1'
        h1 = 'Table editor'

        context_click(self.browser, tree_item)
        self.browser.find_elements_by_class_name('vakata-contextmenu-sep')[0].click()
        wait()
        test_search_value = self.browser.find_element_by_id('search-field').get_attribute('value')
        test_h1 = self.browser.find_elements_by_tag_name('h1')[1].text

        self.assertEqual(test_h1, h1)
        self.assertEqual(test_search_value, search_value)

    def test_tree_redirect_to_entity_site_page(self):
        """Test redirect to entity's site page by context click at tree's item"""
        tree_item = self.browser.find_element_by_id(self.tree_root_node_id).find_element_by_tag_name('a')
        h1 = 'Root category #1'

        context_click(self.browser, tree_item)
        self.browser.find_elements_by_class_name('vakata-contextmenu-sep')[1].click()
        wait()
        test_h1 = self.browser.find_element_by_tag_name('h1').text

        self.assertEqual(test_h1, h1)

    def test_sidebar_toggle(self):
        """Sidebar toggle button storage collapsed state."""

        self.browser.find_element_by_class_name('js-toggle-sidebar').click()
        wait()
        body_classes = self.browser.find_element_by_tag_name('body').get_attribute('class')

        self.assertTrue('collapsed' in body_classes)

        self.browser.refresh()
        wait()
        body_classes = self.browser.find_element_by_tag_name('body').get_attribute('class')

        self.assertTrue('collapsed' in body_classes)

    def test_yandex_feedback_request(self):
        """Send mail with request for leaving feedback on Ya.Market."""

        self.browser.find_element_by_class_name('js-toggle-sidebar').click()
        email_field = self.browser.find_element_by_id('user-email')
        email_field.send_keys(settings.EMAIL_HOST_USER + Keys.RETURN)
        wait()

        self.assertTrue('Письмо с отзывом успешно отправлено' in self.browser.page_source)


class YandexKassa(SeleniumTestCase):
    """Selenium-based tests for YandexKassa"""

    @classmethod
    def setUpClass(cls):
        super(YandexKassa, cls).setUpClass()
        cls.yandex_check = cls.live_server_url + reverse('yandex_check')
        cls.yandex_aviso = cls.live_server_url + reverse('yandex_aviso')

    def test_yandex_check_valid_invoice(self):
        response = self.browser.request('POST',
                                        self.yandex_check,
                                        data={'invoiceId': '42'})
        self.assertTrue('invoiceId="42"' in response.text)


@override_settings(DEBUG=True)
class YandexMetrika(SeleniumTestCase):
    """Selenium-based tests for YandexMetrika"""

    @classmethod
    def setUpClass(cls):
        super(YandexMetrika, cls).setUpClass()

        server = cls.live_server_url
        cls.product_page = server + reverse('product', args=('274',))
        cls.category_page = server + reverse(
            'category', args=('child-1-of-root-category-1',))

    def setUp(self):
        """
        We should use self.browser.get(...) in this case, because we
        faced a problems with it in setUpClass.
        """
        self.browser.get(self.live_server_url)

    @property
    def reached_goals(self):
        """Return yaCounter.goals array after goal triggering."""
        return self.browser.execute_script('return yaCounter.goals;')

    def prevent_default(self, event, selector):
        """Set prevent default for elements so web page wouldn't be reloaded."""
        self.browser.execute_script(
            'var target = document.querySelector("' + selector + '");'
            'target.on' + event + ' = function(event) {'
            'event.preventDefault();'
            'return false;};'
        )

    def test_download_header_price(self):
        """User clicks Download price button in header"""
        self.browser.find_element_by_class_name('js-download-price').click()

        self.assertTrue('PRICE_HEADER' in self.reached_goals)

    def test_download_footer_price(self):
        """User clicks Download price button in footer"""
        self.browser.find_element_by_class_name('js-download-price-footer') \
            .click()

        self.assertTrue('PRICE_FOOTER' in self.reached_goals)

    def test_backcall_open(self):
        """User clicks Back call button"""
        self.browser.find_element_by_class_name('js-backcall-order') \
            .click()

        self.assertTrue('BACK_CALL_OPEN' in self.reached_goals)

    def test_browse_product_open(self):
        """User browses to product's page"""
        self.browser.get(self.category_page)
        self.prevent_default('click', '.js-browse-product')
        self.browser.find_element_by_class_name('js-browse-product') \
            .click()

        self.assertTrue('PROD_BROWSE' in self.reached_goals)

    def test_add_product_from_product_page(self):
        """User adds product to cart on Product's page"""
        self.browser.get(self.product_page)
        self.browser.find_element_by_class_name('js-to-cart-on-product-page') \
            .click()

        self.assertTrue('PUT_IN_CART_FROM_PRODUCT' in self.reached_goals)
        self.assertTrue('CMN_PUT_IN_CART' in self.reached_goals)

    def test_add_product_from_category_page(self):
        """"User adds product to cart on Category's page"""
        self.browser.get(self.category_page)
        self.browser.find_element_by_class_name('js-product-to-cart').click()

        self.assertTrue('PUT_IN_CART_FROM_CATEGORY' in self.reached_goals)
        self.assertTrue('CMN_PUT_IN_CART' in self.reached_goals)

    def test_delete_product(self):
        """User removes product from cart"""
        self.browser.get(self.product_page)
        self.browser.find_element_by_class_name('js-to-cart-on-product-page') \
            .click()
        wait()
        self.browser.find_element_by_class_name('js-go-to-cart').click()
        self.browser.find_element_by_class_name('js-remove').click()

        self.assertTrue('DELETE_PRODUCT' in self.reached_goals)

    def test_use_search(self):
        """User uses search field"""
        self.prevent_default('submit', '.js-search-form')
        self.browser.find_element_by_class_name('js-search-form').submit()

        self.assertTrue('USE_SEARCH_FORM' in self.reached_goals)


class Search(SeleniumTestCase):
    """Selenium-based tests for Search"""

    QUERY = 'Cate'

    def setUp(self):
        """
        We should use self.browser.get(...) in this case, because we
        faced a problems with it in setUpClass.
        """
        self.browser.get(self.live_server_url)
        wait()

    @property
    def autocomplete(self):
        return self.browser.find_element_by_class_name(
            'autocomplete-suggestions')

    @property
    def input(self):
        return self.browser.find_element_by_class_name('js-search-input')

    def fill_input(self):
        """Enter correct search term"""
        self.input.send_keys(self.QUERY)
        wait()

    def clear_input(self):
        """Enter correct search term"""
        self.input.send_keys(Keys.BACKSPACE*len(self.QUERY))
        wait()

    def test_autocomplete_can_expand_and_collapse(self):
        """
        Autocomplete should minimize during user typing correct search query
        Autocomplete should minimize by removing search query
        """
        wait()
        self.fill_input()
        # fill input and autocomplete expands
        self.assertTrue(self.autocomplete.is_displayed())

        # remove search term ...
        self.input.send_keys(Keys.BACKSPACE * len(self.QUERY))
        wait()
        # ... and autocomplete collapse
        self.assertFalse(self.autocomplete.is_displayed())
        self.clear_input()

    def test_autocomplete_item_link(self):
        """First autocomplete item should link on category page by click"""
        self.fill_input()
        first_item = self.autocomplete.find_element_by_css_selector(
            ':first-child')
        first_item.click()
        wait()
        self.assertTrue('/catalog/categories/' in self.browser.current_url)
        self.clear_input()

    def test_autocomplete_see_all_item(self):
        """
        Autocomplete should contain "see all" item.
        "See all" item links on search results page
        """
        self.fill_input()
        last_item = self.autocomplete.find_element_by_class_name(
            'autocomplete-last-item')
        last_item.click()
        wait()
        self.assertTrue('/search/' in self.browser.current_url)
        self.clear_input()

    def test_search_have_results(self):
        """Search results page should contain links on relevant pages"""
        self.fill_input()
        search_form = self.browser.find_element_by_class_name('search-form')
        search_form.submit()
        wait()
        self.assertTrue(self.browser.find_element_by_link_text(
            'Child #0 of #Root category #0'))
        self.assertTrue(self.browser.find_element_by_link_text(
            'Child #1 of #Root category #0'))
        self.clear_input()

    def test_search_results_empty(self):
        """Search results for wrong term should contain empty result set"""
        self.input.send_keys('Not existing search query')
        button_submit = self.browser.find_element_by_id('search-submit')
        button_submit.click()
        wait()
        h1 = self.browser.find_element_by_tag_name('h1')
        self.assertTrue(h1.text == 'По вашему запросу ничего не найдено')
        self.clear_input()