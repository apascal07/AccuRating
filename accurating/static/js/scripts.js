(function($){
  $('.training-set-list').waterfall();
  var products = $('.product-item');
  $('.select-all').on('change', function(e){
    var state = $(this).is(':checked');
    $('.select-product', products).prop('checked', state);
  });
})(jQuery);
