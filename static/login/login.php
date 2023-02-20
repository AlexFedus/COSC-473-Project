<?php

$data = $_POST;

// validate required fields
$errors = [];
foreach (['email', 'password'] as $field) {
    if (empty($data[$field])) {
        $errors[] = sprintf(format: 'The %s is a required field.', $field);
    }
}

if (!empty($errors)) {
    echo implode(separator: '<br />', $errors);
    exit;
}

$nm = $data['email'];
if (!filter_var($email, filter:FILTER_VALIDATE_EMAIL)) {
    echo 'Invalid email format';
    exit;
}

//database connection
$host = 'sql9.freesqldatabase.com';
$database = 'sql9598812';
$user = 'sql9598812';
$password = 'uJVAVztfRj';
$dsn = sprintf(format: "mysql:host=%s;dbname=%s", $host, $database);

$options = [
    PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
    PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,   
];
try {
    $pdo = new PDO($dsn, $user, $password, $options);
} catch (\PDOException $e) {
    throw new \PDOException($e->getMessage(), (int)$e->getCode());
}

// check email
$statement = $pdo->prepare(query: 'SELECT * FROM test WHERE email = :email');
$statement->execute(['email' => $data['email']]);

if (!empty($statement->fetch())) {
    echo 'User with this email already exists.';
    exit;
}

// insert new user
$statement = $pdo->prepare(
    query: 'INSERT INTO test (email, password) VALUES (:email, :password)'
);

$statement->execute([
    'email' => $test['email'],
    'password' => password_hash($test['password'], algo:PASSWORD_BCRYPT)
]);

echo 'User account has been created.';

?>
