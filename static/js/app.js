$(function(){
  $('.edit').on('click', function(){
    var id = $(this).siblings().find(".category-name").data('category-id');
    var url = $SCRIPT_ROOT + '/catalog/' + id +'/edit'
    $.getJSON(url, function(category){
      $('#editModal').find('input[name="name"]').val(category.name);
      $('#editModal').find('form').attr('action', url);
    });
  });
});

$(".alert").fadeTo(2000, 500).slideUp(500, function(){
    $(this).slideUp(500);
});
