$(".alert").fadeTo(3000, 500).slideUp(500, function(){
  $(this).slideUp(500);
});

$(function(){
  $('.edit').on('click', function(){
    var id = $(this).siblings().find(".category-name").data('category-id');
    var url = $SCRIPT_ROOT + '/catalog/' + id +'/edit';
    $.getJSON(url, function(category){
      $('#editModal').find('input[name="name"]').val(category.name);
      $('#editModal').find('form').attr('action', url);
    });
  });
});

$(function(){
  $('.delete').on('click', function(){
    var id = $(this).siblings().find(".category-name").data('category-id');
    var url = $SCRIPT_ROOT + '/catalog/' + id +'/delete';
    $("#deleteModalLabel").text("Delete Category");
    $.getJSON(url, function(category){
      $('#deleteModal').find('input[name="name"]').val(category.name);
      $('#deleteModal').find('form').attr('action', url);
      $('.delete-message').text("Are you sure you want to delete the " +
        category.name + " cateogry?" );
    });
  });
});

$(function(){
  $('.item-container .delete-item').on('click', function(){
    var name = $(this).parent().data('item-name');
    var categoryName = $(this).parent().siblings('.description').text().trim();
    $("#deleteModalLabel").text("Delete Item");
    var url = $SCRIPT_ROOT + '/catalog/' + categoryName + '/' + name +'/delete';
    $.getJSON(url, function(item){
      $("#deleteModalLabel").text("Delete Item")
      $('#deleteModal').find('input[name="name"]').val(item.name);
      $('#deleteModal').find('form').attr('action', url);
      $('.delete-message').text("Are you sure you want to delete " +
        item.name + " from " + item.category + "?" );
    });
  });
});

$(function(){
  $('.categories-container .metal').on('click', function(){
    var category = $(this).children().text().trim();
    var url = $SCRIPT_ROOT + '/catalog/' + category + "/items";
    $.ajax({
      url: url,
      type: "get",
      success: function(response) {
        $(".item-container .list-group").html(response);
        $(".item-container")
          .parents('fieldset').children('legend').text(category);
      },
      error: function(xhr) {
        $(".item-container .list-group").append(
            $('<li>!!!Something went poorly!!!</li>')
              .addClass('list-group-item error-li'));
      }
    });
  });
});

$('.item-container').on('click', '.preview-item', function(){
  var item = $(this).parent('div').data("item-name");
  var category = $(this).parents('.list-group-item')
                    .children('.description').text().trim();
  var url = $SCRIPT_ROOT + '/catalog/' + category + "/" + item;
  $.getJSON(url, function(item){
    if(item.message){
      $(".error-li").text(item.message)
    } else {
      $("#previewModalLabel").text(item.name);
      $("#itemImage").attr('src', item.picture);
      $(".item-description").text(item.description);
    }
  });
});
