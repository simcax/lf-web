# Database structure

## Tables
|tablename|content|
|---------|-------|
|index|Contains the overall index for building the navigation|
|pages|Table holding information about the page contenst|
|md|This table contains the actual markdown, which makes up a pages content|

## index

|field|
|-----|
|id|row id|
|parent_id|id of the parent page (top menu item)|
|sub_page_id|id of the sub_page|

## pages

|field|content|
|-----|-------|
|id|row id|
|title|title shown in the menu|
|url|url the page goes to when clicked|
|sub_page|bool - is it a sub_page?|

## md

|field|content|
|-----|-------|
|id|row id|
|page_id|id of the pages row|
|md|markdown content|
