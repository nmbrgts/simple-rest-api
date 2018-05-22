## Trying the API
Here is a sort of quick start guide for trying out the API with a number of example requests and their results.

### Creating A User

`POST` to `/api/v1/users` to create a user. Note that all other `POST` actions require a basic `Authorization` header to access. To play with the API you can either use the example account or create your own.

Example request:
```json
{
    "username": "dvader",
    "password": "luke+lea4eva",
    "verify_password": "luke+lea4eva",
    "email": "vader@deathstar.com"
}
```
Example response:
```json
{
    "email": "vader@deathstar.com",
    "id": 1,
    "password": "luke+lea4eva",
    "username": "dvader"
}
```

### Adding A Course

`POST` to `api/v1/courses` to add a course.

Example request:
```json
{
    "title": "Machine Learning  - Coursera/Stanford, Andrew Ng"
    "url": "https://www.coursera.org/learn/machine-learning"
}
```

Example response:
```json
{
    "id": 1,
    "reviews": [],
    "tags": [],
    "title": "Machine Learning  - Coursera/Stanford, Andrew Ng",
    "url": "https://www.coursera.org/learn/machine-learning"
}
```

### Adding Tags

`POST` to `/api/v1/addtag` to add a tag to a course.

Example request body:
```json
{
    "tag": "Machine Learning",
    "course": "/api/v1/courses/1"
}
```

Example response:
```json
""
```
The response is empty. This is partly because adding a tag touches a lot of back end stuff that I didn't feel the API should expose. Instead, the `Location` header will contain the url to the updated course.

Example course:
```json
{
    "id": 1,
    "reviews": [],
    "tags": [
        "Machine Learning"
    ],
    "title": "Machine Learning  - Coursera/Stanford, Andrew Ng",
    "url": "https://www.coursera.org/learn/machine-learning"
}
```

### Adding Reviews

`POST` to `/api/v1/reviews` to add reviews.

Example request:
```json
{
    "course": 1,
    "rating": 5,
    "comment": "Excellent introductory course with challengine coding exercises. Only draw back is that the course is in MatLab / Octave which is no longer a popular language for ML."
}
```

Example response:
```json
{
    "by_user": "/api/v1/users/1",
    "child_comments": [],
    "comment": "Excellent introductory course with challengine coding exercises. Only draw back is that the course is in MatLab / Octave which is no longer a popular language for ML.",
    "created_at": "2018-05-21T21:53:16.436480",
    "down_votes": 0,
    "for_course": "/api/v1/courses/1",
    "id": 1,
    "rating": 5,
    "up_votes": 0
}
```

### Adding Comments

`POST` to `/api/v1/comments` to add comments. Comments can target either reviews or other comments. This is handled through optional fields `parent_comment` for comments and `review` for reviews.

Example request:
```json
{
    "review": 1,
    "comment": "Couldn't agree more. Ng's course is an excellent resource!"
}
```

Example response:
```json
{
    "by": "/api/v1/users/2",
    "children": [],
    "comment": "Couldn't agree more. Ng's course is an excellent resource!",
    "date": "2018-05-21T23:22:43.553565",
    "down_votes": 0,
    "parent_comment": null,
    "review": "/api/v1/reviews/1",
    "up_votes": 0
}
```

Example request:
```json
{
    "parent_comment": 1,
    "comment": "Thanks for the kind comment!"
}
```

Example response:
```json
{
    "by": "/api/v1/users/1",
    "children": [],
    "comment": "Thanks for the kind comment!",
    "date": "2018-05-21T23:26:06.100535",
    "down_votes": 0,
    "parent_comment": "/api/v1/comments/1",
    "review": null,
    "up_votes": 0
}
```

If we check the parent comment, we can see that it now lists the second comment as one of it's children.
```json
{
    "by": "/api/v1/users/2",
    "children": [
        "/api/v1/comments/2"
    ],
    "comment": "Couldn't agree more. Ng's course is an excellent resource!",
    "date": "2018-05-21T23:22:43.553565",
    "down_votes": 0,
    "parent_comment": null,
    "review": "/api/v1/reviews/1",
    "up_votes": 0
}
```

### Adding Up/Downvotes

To upvote `POST` to `api/v1/upvote`, to downvote `POST` to `api/v1/downvote`. The only parameter that needs to be supplied is `url` which is the endpoint uri or url for the comment or review you wish to upvote/downvote.

Example request:
```json
{
    "url": "/reviews/1"
}
```

Example response:
```json
""
```

Similar to tags, the response body is empty but, the `Location` header points to the updated review/comment. We can see the change if we `GET` the `Location` url:

```json
{
    "by_user": "/api/v1/users/1",
    "child_comments": [
        "/api/v1/comments/1"
    ],
    "comment": "Excellent introductory course with challengine coding exercises. Only draw back is that the course is in MatLab / Octave which is no longer a popular language for ML.",
    "created_at": "2018-05-21T21:53:16.436480",
    "down_votes": 0,
    "for_course": "/api/v1/courses/1",
    "id": 1,
    "rating": 5,
    "up_votes": 1
}
```
