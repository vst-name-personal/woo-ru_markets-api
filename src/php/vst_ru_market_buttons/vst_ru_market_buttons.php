<?php

/**
 * Plugin Name: VST RU Market buttons
 * Plugin URI: https://vst.name/
 * Description: Creates buttons to russian markets according to url attributes.
 * Version: 0.1
 * Author: VST
 * Author URI: https://vst.name/
 **/
function get_acf_field_group_by_name($group_name)
{
    $groups = acf_get_field_groups();
    foreach ($groups as $group) {
        if ($group['title'] === $group_name) {
            return $group;
        }
    }
    return null;
}
function CreateBtns() {
    global $product;
    // Assuming $product is an instance of the product, and the meta_data is already available as an array
    $ym_counter = (string)"95836115";
    // Define the market meta keys in the product's meta_data
    $MarketKeys = array("ozon_url", "wb_url", "ym_url", "mm_url", "vk_url");
    $group_names = array("Свойства товара");
    $group_data = array();
    if (function_exists('acf_get_field_group')) {
        $group_name = 'Свойства товара'; // Replace with your actual field group name
        $field_group = get_acf_field_group_by_name($group_name);

        if ($field_group) {
            $group_id = $field_group['ID'];
            $group_data = acf_get_fields($group_id);
            #print_r($group_data);
        }
    }
    // Output the CSS from the stylesheet
    $css_contents = file_get_contents(plugin_dir_path(__FILE__) . 'css/btns.css');
    echo '<style>' . $css_contents . '</style>';
    // Output the market buttons HTML
    echo '<div id="market_btns" class="market_btns">';
    foreach ($MarketKeys as $marketKey) {
        $m_url = $product->get_meta($marketKey);
        if ($m_url == "None") {
            $m_url = $group_data[$marketKey];
            $product_sku = $product->get_sku();
        }
        if (!empty($m_url) && strcmp($m_url, "Unavailable") != 0 && strcmp($m_url, "None") != 0) {
            // Create a new cell element for the button
            $type = $marketKey;
            $type_text = "";
            $metrika_btn_name = "";
            $product_name = $product->get_title();
            $metrika_ar = array(
                'element.market_btns' => array(
                    $product_name => array(
                        'sku' => $product->get_sku(),
                        'btn_type' => $type,
                        'url_origin' => $_SERVER['REQUEST_URI'],
                        'url_destination' => $m_url
                    )
                )
            );

            switch ($type) {
                case "wb_url":
                    $type_text = "WildBerries";
                    $metrika_btn_name = "wb_btn_click";
                    break;

                case "ozon_url":
                    $type_text = "Ozon";
                    $metrika_btn_name = "ozon_btn_click";
                    break;

                case "ym_url":
                    $type_text = "Яндекс Маркет";
                    $metrika_btn_name = "ym_btn_click";
                    break;

                case "mm_url":
                    $type_text = "МегаМаркет";
                    $metrika_btn_name = "mm_btn_click";
                    break;

                case "vk_url":
                    $type_text = "Вконтакте";
                    $metrika_btn_name = "vk_btn_click";
                    break;

                case "tmp":
                    $type_text = "To be...";
                    $metrika_btn_name = "tmp_btn_click";
                    break;
            }

            $newBtn = '<div class="market_btns ' . $type . '_btn ' . $type . '_btn_visible fade-in">';
            $newBtn .= '<a class="' . $type . '_btn" ';
            if (!str_starts_with($m_url, "https://")) {
                $m_url = "https://" . $m_url;
            }
            if (str_contains($m_url, "utm_campaign")) {
                $m_url .= '&utm_content=' . $product_name . '&utm_term=' . $type;
            } elseif (!str_contains($m_url, "utm_source")) {
                $m_url .= '?utm_source=site&utm_medium=market_btns&utm_campaign=' . $product_name . '&utm_content=' . $type;
            }

            $newBtn .= 'href="' . $m_url . '" onclick="';
            $newBtn .= 'ym(' . $ym_counter . ', \'reachGoal\', \'' . $metrika_btn_name . '\', ' . htmlspecialchars(json_encode($metrika_ar), ENT_QUOTES, 'UTF-8') . ');';
            $newBtn .= 'ym(' . $ym_counter . ', \'reachGoal\', \'market_btn_click\', ' . htmlspecialchars(json_encode($metrika_ar), ENT_QUOTES, 'UTF-8') . ');';
            $newBtn .= 'return true;"';
            $newBtn .= ' target="_blank" rel="nofollow noopener dns-prefetch">';

            $newBtn .= '<img class="market_btns_img" src="/wp-content/uploads/vst_market_btns/' . $type . '.svg" alt="Наш товар в ' . $type_text . '"></img>';
            $newBtn .= '<span>' . ucfirst($type_text) . '</span>';
            $newBtn .= '</a>';
            $newBtn .= '</div>';

            echo $newBtn;
        }
    }
    echo '</div>';
    $cat_link = add_category_link();
    echo $cat_link;
}

function add_sku() {
    global $product;
    echo '<span style="display: block; text-align: right">' . $product->get_sku() . '</span>';
}

function remove_additional_info_tab($tabs) {
    unset($tabs['additional_information']); // To remove the additional information tab
    return $tabs;
}

function add_custom_product_tab($tabs) {
    $tabs['docs'] = array(
        'title' => __('Свойства товара', 'woocommerce'), // TAB TITLE
        'priority' => 20, // TAB SORTING (DESC 10, ADD INFO 20, REVIEWS 30)
        'callback' => 'add_custom_product_tab_content', // TAB CONTENT CALLBACK
    );
    return $tabs;
}

function add_custom_product_tab_content() {
    global $product;
    $field_groups = array('group_65ba0b953c6cd', 'group_65bb8538949d9', 'group_65bb8312b4873');
    $css_contents = file_get_contents(plugin_dir_path(__FILE__) . 'css/product_additional_info.css');
    $result_html = '<style>' . $css_contents . '</style>';

    $max_width = 0;
    $max_width_const = 10;
    $product_attributes = $product->get_attributes();

    $attributes_kv = array();
    foreach ($product_attributes as $attribute) {
        if (!$attribute->get_variation() && !$attribute->get_visible()) {
            continue;
        }

        $attribute_name = wc_attribute_label($attribute->get_name(), $product);
        $term_options = array();

        foreach ($attribute->get_options() as $option) {
            $term = get_term($option, $attribute->get_name());
            $term_options[] = $term ? $term->name : $option;
        }

        $attributes_kv[$attribute_name] = esc_html(implode(', ', $term_options));

        $max_width = max($max_width, strlen($attribute_name) * $max_width_const);
    }

    $first_block = false;

    foreach ($field_groups as $field_group) {
        $acf_fields = acf_get_fields($field_group, $product->get_id());
        if (empty($acf_fields)) {
            continue;
        }
        $field_group_obj = acf_get_field_group($field_group);
        $group_name = $field_group_obj['title'];
        $result_html .= '<div class="acf-group">';
        $result_html .= '<h2 class="acf-group-title">' . esc_html($group_name) . '</h2>';

        if (!$first_block) {
            foreach ($attributes_kv as $acf_label => $acf_value) {
                $max_width = max($max_width, strlen($acf_label) * $max_width_const); 

                $result_html .= '<div class="acf-row">';
                $result_html .= '<div class="acf-key" style="max-width: ' . $max_width . 'px;">' . esc_html($acf_label) . '</div>';
                $result_html .= '<div class="acf-value">' . esc_html($acf_value) . '</div>';
                $result_html .= '</div>';
            }

            $first_block = true;
        }

        if ($acf_fields && is_array($acf_fields)) {
            foreach ($acf_fields as $acf_field) {
                $acf_label = $acf_field['label'];
                $acf_key = $acf_field['name'];
                $acf_value = get_field($acf_key, $product->get_id());
                $link = false;

                if (str_starts_with($acf_value, 'http') == true) {
                    $acf_value = '<a href="' . $acf_value . '" target="_blank" rel="noopener noreferrer">открыть</a>';
                    $link = true;
                }

                $max_width = max($max_width, strlen($acf_label) * 10);

                $result_html .= '<div class="acf-row">';
                $result_html .= '<div class="acf-key" style="max-width: ' . $max_width . 'px;">' . esc_html($acf_label) . '</div>'; // Display the key
                $result_html .= '<div class="acf-value">' . ($link ? $acf_value : esc_html($acf_value)) . '</div>'; // Display the value
                $result_html .= '</div>';
            }

            $result_html .= '</div>';
        }
    }
    
    echo $result_html;

}

function add_category_link() {
    global $product;

    // Get the product categories
    $categories = get_the_terms($product->get_id(), 'product_cat');
    
    // Check if there are categories
    if ($categories && !is_wp_error($categories)) {
        // Find the top-level parent category
        $top_level_parent = 0;
    
        foreach ($categories as $category) {
            $ancestors = get_ancestors($category->term_id, 'product_cat');
    
            if (empty($ancestors)) {
                $top_level_parent = $category->term_id;
                break;
            }
        }
    
        // Output the top-level parent category name with a link
        if ($top_level_parent) {
            $top_level_category = get_term($top_level_parent, 'product_cat');
            $result = '<div class="cat-btn"><a href="' . get_term_link($top_level_category->term_id, 'product_cat') . '">' . 'Посмотреть всю категорию: ' . mb_strtolower($top_level_category->name) . '</a></div>';
            $css_contents = file_get_contents(plugin_dir_path(__FILE__) . 'css/cat_btn.css');
            $result .=  '<style>' . $css_contents . '</style>';
            return $result;
        }
    }
}
function enqueue_custom_styles() {
    if (is_product()) {
        #wp_enqueue_style('btns-style', plugin_dir_url(__FILE__) . 'css/btns.css');
        wp_enqueue_style('linked-variations-style', plugin_dir_url(__FILE__) . 'css/linked-variations.css');
    }
}

add_action('wp_enqueue_scripts', 'enqueue_custom_styles');

add_filter('woocommerce_product_tabs', 'remove_additional_info_tab', 25);
add_filter('woocommerce_product_tabs', 'add_custom_product_tab', 20);
add_action('woocommerce_single_product_summary', 'add_sku', 10);
add_action('astra_woo_single_title_after', 'CreateBtns', 10);
add_filter('pre_option_elementor_maintenance_mode_mode', function ($option) {
    $parameter = 'el-bypass';
    $parameter_value = '1';

    $search_engine_user_agents = ['Googlebot', 'Bingbot', 'Slurp', 'DuckDuckBot'];

    $is_search_engine = false;
    foreach ($search_engine_user_agents as $bot) {
        if (strpos($_SERVER['HTTP_USER_AGENT'], $bot) !== false) {
            $is_search_engine = true;
            break;
        }
    }

    if (isset($_GET[$parameter]) || (isset($_COOKIE[$parameter]) && $_COOKIE[$parameter] === $parameter_value) || $is_search_engine) {
        setcookie($parameter, $parameter_value, [
            'expires' => time() + 3600 * 24 * 7,
            'path' => '/',
            'domain' => 'cleanyear.ru',
            'secure' => true,
            'httponly' => true,
            'samesite' => 'Strict',
        ]);

        return 0;
    }

    return $option;
});


?>