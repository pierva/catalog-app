# Catalog App

### Routes specification
HOME => Shows all categories on the left and last added items

`/` <br>
`catalog`


ADD CATEGORY ['POST'] => Add a category in the catalog

`/catalog/new`

EDIT CATEGORY ['PUT'] => Edit a category in the catalog

`/catalog/edit `

DELETE CATEGORY ['DELETE'] => Delete the category in the catalog

`/catalog/edit`

CATEGORY => Shows the items for that specific category

`/catalog/<str:category-name>/`
`/catalog/<str:category-name>/items`

ITEM ['GET']=> Get item details

`/catalog/<str:category-name>/<str:item-name>`

ITEM ['POST'] => Add a new item

`/catalog/<str:category-name>/new`

ITEM ['PUT'] => Edit an item

`/catalog/<str:category-name>/<str:item-name>/edit`

ITEM ['PUT'] => Delete an item

`/catalog/<str:category-name>/<str:item-name>/delete`


### API ENDPOINTS

Get all the information in the database:

`/catalog/api/v1/all/JSON`

Get the list of available categories

`/catalog/api/v1/categories/JSON`

Get items of a specific category

`/catalog/api/v1/<str:category-name>/items/JSON` <br>
`/catalog/api/v1/<int:category-id>/items/JSON`

Get item description
`/catalog/api/v1/<str:category-name>/<str:item-name>/description/JSON` <br>
`/catalog/api/v1/<int:category-id>/<int:item-id>/description/JSON`
