# Catalog App

### Routes specification
HOME => Shows all categories on the left and last added items

`/` <br>
`catalog`


ADD CATEGORY ['POST'] => Add a category in the catalog

`/catalog/new`

EDIT CATEGORY ['PUT'] => Edit a category in the catalog

`/catalog/<categoryName>/edit `

DELETE CATEGORY ['DELETE'] => Delete the category in the catalog

`/catalog/<categoryName>/delete`

CATEGORY => Shows the items for that specific category

`/catalog/<categoryName>/` <br>
`/catalog/<categoryName>/items`

ITEM ['GET']=> Get item details

`/catalog/<categoryName>/<itemName>`

ITEM ['POST'] => Add a new item

`/catalog/<categoryName>/new`

ITEM ['PUT'] => Edit an item

`/catalog/<categoryName>/<itemName>/edit`

ITEM ['PUT'] => Delete an item

`/catalog/<categoryName>/<itemName>/delete`


### API ENDPOINTS

Get all the information in the database:

`/catalog/api/v1/all/JSON`

Get the list of available categories

`/catalog/api/v1/categories/JSON`

Get items of a specific category

`/catalog/api/v1/<categoryName>/items/JSON` <br>
`/catalog/api/v1/<int:category-id>/items/JSON`

Get item description
`/catalog/api/v1/<categoryName>/<itemName>/description/JSON` <br>
`/catalog/api/v1/<int:category-id>/<int:item-id>/description/JSON`
