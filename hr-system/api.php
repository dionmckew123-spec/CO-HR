<?php

declare(strict_types=1);

header('Content-Type: application/json');
header('Cache-Control: no-store, no-cache, must-revalidate, max-age=0');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, PUT, PATCH, DELETE, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(204);
    exit;
}

$dataFile = __DIR__ . '/data/employees.json';

if (!file_exists($dataFile)) {
    file_put_contents($dataFile, json_encode([], JSON_PRETTY_PRINT));
}

function loadEmployees(string $file): array
{
    $contents = file_get_contents($file);
    if ($contents === false || $contents === '') {
        return [];
    }

    $decoded = json_decode($contents, true);
    return is_array($decoded) ? $decoded : [];
}

function saveEmployees(string $file, array $employees): void
{
    file_put_contents($file, json_encode($employees, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
}

function getJsonInput(): array
{
    $raw = file_get_contents('php://input');
    if ($raw === false || $raw === '') {
        return $_POST ? $_POST : [];
    }

    $data = json_decode($raw, true);
    if (json_last_error() !== JSON_ERROR_NONE) {
        return [];
    }

    return $data;
}

$employees = loadEmployees($dataFile);

switch ($_SERVER['REQUEST_METHOD']) {
    case 'GET':
        echo json_encode(['data' => $employees]);
        break;

    case 'POST':
        $payload = getJsonInput();
        $required = ['name', 'department', 'role', 'email', 'status', 'startDate'];
        foreach ($required as $field) {
            if (!isset($payload[$field]) || trim((string) $payload[$field]) === '') {
                http_response_code(422);
                echo json_encode(['error' => "Missing or empty field: {$field}"]);
                exit;
            }
        }

        $ids = array_column($employees, 'id');
        $nextId = $ids ? max($ids) + 1 : 1;

        $employees[] = [
            'id' => $nextId,
            'name' => trim($payload['name']),
            'department' => trim($payload['department']),
            'role' => trim($payload['role']),
            'email' => trim($payload['email']),
            'status' => trim($payload['status']),
            'startDate' => trim($payload['startDate']),
        ];

        saveEmployees($dataFile, $employees);
        echo json_encode(['data' => end($employees)]);
        break;

    case 'PUT':
    case 'PATCH':
        $payload = getJsonInput();
        if (!isset($payload['id'])) {
            http_response_code(422);
            echo json_encode(['error' => 'Missing employee id']);
            exit;
        }

        $updated = false;
        foreach ($employees as &$employee) {
            if ((int) $employee['id'] === (int) $payload['id']) {
                foreach (['name', 'department', 'role', 'email', 'status', 'startDate'] as $field) {
                    if (isset($payload[$field])) {
                        $employee[$field] = trim((string) $payload[$field]);
                    }
                }
                $updated = true;
                break;
            }
        }
        unset($employee);

        if (!$updated) {
            http_response_code(404);
            echo json_encode(['error' => 'Employee not found']);
            exit;
        }

        saveEmployees($dataFile, $employees);
        echo json_encode(['data' => $employees]);
        break;

    case 'DELETE':
        $payload = getJsonInput();
        if (!isset($payload['id'])) {
            http_response_code(422);
            echo json_encode(['error' => 'Missing employee id']);
            exit;
        }

        $originalCount = count($employees);
        $employees = array_values(array_filter(
            $employees,
            static fn ($emp): bool => (int) $emp['id'] !== (int) $payload['id']
        ));

        if ($originalCount === count($employees)) {
            http_response_code(404);
            echo json_encode(['error' => 'Employee not found']);
            exit;
        }

        saveEmployees($dataFile, $employees);
        echo json_encode(['data' => $employees]);
        break;

    default:
        http_response_code(405);
        echo json_encode(['error' => 'Method not allowed']);
        break;
}
