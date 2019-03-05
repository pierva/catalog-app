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
      $('.delete-message').text("Are you sure you want to delete " +
        category.name + " cateogry?" );
    });
  });
});

$(function(){
  $('.item-container button').on('click', function(){
    var name = $(this).parent().data('item-name');
    var categoryName = $(this).parent().siblings('.description').text().trim();
    $("#deleteModalLabel").text("Delete Item");
    var url = $SCRIPT_ROOT + '/catalog/' + categoryName + '/' + name +'/delete';
    $.getJSON(url, function(item){
      $("#deleteModalLabel").text("Delete Category")
      $('#deleteModal').find('input[name="name"]').val(item.name);
      $('#deleteModal').find('form').attr('action', url);
      $('.delete-message').text("Are you sure you want to delete " +
        item.name + " from " + item.category + "?" );
    });
  });
});
