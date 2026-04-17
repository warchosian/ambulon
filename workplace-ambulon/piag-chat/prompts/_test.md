```plantuml
participant Alice
participant Bob
note left of Alice #aqua
This is displayed
left of Alice.
end note

note over Alice
 This is displayed right of Alice.
end note 

note over Alice: This is displayed over Alice.

note over Alice, Bob #FFAAAA: This is displayed\n over Bob and Alice.

note over Bob, Alice
This is yet another
example of
a long note.
end note
```