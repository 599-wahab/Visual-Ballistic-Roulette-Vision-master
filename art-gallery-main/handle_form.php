<?php
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    // Check if all fields are not empty
    if (!empty($_POST["Name"]) && !empty($_POST["Email"]) && !empty($_POST["feedback"])) {
        // Check if email contains "@gmail.com"
        if (strpos($_POST["Email"], "@gmail.com") !== false) {
            // All conditions met, process the form
            $name = $_POST["Name"];
            $email = $_POST["Email"];
            $feedback = $_POST["feedback"];
            
            // Here you can perform further actions like sending an email, storing data in a database, etc.
            
            // For demonstration, let's just print the form data
            echo "Name: $name<br>";
            echo "Email: $email<br>";
            echo "Feedback: $feedback<br>";
        } else {
            echo "Invalid email address. Please enter a Gmail address.";
        }
    } else {
        echo "All fields are required.";
    }
}
?>