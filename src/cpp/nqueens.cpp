#include <chrono>
#include <cstdint>
#include <fstream>
#include <functional>
#include <iostream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

using Result = std::pair<std::uint64_t, std::uint64_t>;

struct Instance {
    int n;
    std::vector<int> fixed;
};

Instance read_instance(const std::string& path) {
    std::ifstream input(path);
    int n, k;
    if (!(input >> n >> k) || n < 1 || k < 0 || k > n) {
        throw std::runtime_error("formato invalido");
    }
    std::vector<int> fixed(n, -1);
    for (int i = 0; i < k; ++i) {
        int row, col;
        if (!(input >> row >> col) || row < 0 || row >= n || col < 0 || col >= n || fixed[row] != -1) {
            throw std::runtime_error("posicao fixa invalida ou linha repetida");
        }
        fixed[row] = col;
    }
    std::string extra;
    if (input >> extra) {
        throw std::runtime_error("dados excedentes");
    }
    return {n, std::move(fixed)};
}

bool valid_fixed(const std::vector<int>& fixed) {
    const int n = static_cast<int>(fixed.size());
    std::vector<std::uint8_t> cols(n), down(2 * n - 1), up(2 * n - 1);
    for (int row = 0; row < n; ++row) {
        const int col = fixed[row];
        if (col < 0) continue;
        const int d = row - col + n - 1;
        const int u = row + col;
        if (cols[col] || down[d] || up[u]) return false;
        cols[col] = down[d] = up[u] = 1;
    }
    return true;
}

Result brute_force(const Instance& instance) {
    const int n = instance.n;
    if (!valid_fixed(instance.fixed)) return {0, 0};
    std::vector<int> free_rows, free_cols, board = instance.fixed;
    std::vector<std::uint8_t> fixed_cols(n), used(n);
    for (int row = 0; row < n; ++row) {
        if (instance.fixed[row] < 0) free_rows.push_back(row);
        else fixed_cols[instance.fixed[row]] = 1;
    }
    for (int col = 0; col < n; ++col) {
        if (!fixed_cols[col]) free_cols.push_back(col);
    }
    std::uint64_t count = 0, leaves = 0;
    std::function<void(int)> visit = [&](int depth) {
        if (depth == static_cast<int>(free_rows.size())) {
            ++leaves;
            std::vector<std::uint8_t> down(2 * n - 1), up(2 * n - 1);
            bool conflict = false;
            for (int row = 0; row < n; ++row) {
                const int col = board[row];
                const int d = row - col + n - 1;
                const int u = row + col;
                if (down[d] || up[u]) conflict = true;
                down[d] = up[u] = 1;
            }
            if (!conflict) ++count;
            return;
        }
        const int row = free_rows[depth];
        for (int j = 0; j < static_cast<int>(free_cols.size()); ++j) {
            if (used[j]) continue;
            used[j] = 1;
            board[row] = free_cols[j];
            visit(depth + 1);
            used[j] = 0;
        }
    };
    visit(0);
    return {count, leaves};
}

Result backtracking(const Instance& instance) {
    const int n = instance.n;
    if (!valid_fixed(instance.fixed)) return {0, 0};
    std::vector<std::uint8_t> cols(n), down(2 * n - 1), up(2 * n - 1);
    std::uint64_t count = 0, attempts = 0;
    std::function<void(int)> visit = [&](int row) {
        if (row == n) {
            ++count;
            return;
        }
        const int first = instance.fixed[row] < 0 ? 0 : instance.fixed[row];
        const int last = instance.fixed[row] < 0 ? n : first + 1;
        for (int col = first; col < last; ++col) {
            ++attempts;
            const int d = row - col + n - 1;
            const int u = row + col;
            if (cols[col] || down[d] || up[u]) continue;
            cols[col] = down[d] = up[u] = 1;
            visit(row + 1);
            cols[col] = down[d] = up[u] = 0;
        }
    };
    visit(0);
    return {count, attempts};
}

int main(int argc, char** argv) {
    try {
        if (argc < 3) throw std::runtime_error("uso: nqueens <brute|backtracking> <entrada> [repeticoes] [aquecimento]");
        const std::string algorithm = argv[1];
        if (algorithm != "brute" && algorithm != "backtracking") throw std::runtime_error("algoritmo invalido");
        const int repetitions = argc >= 4 ? std::stoi(argv[3]) : 1;
        const int warmup = argc >= 5 ? std::stoi(argv[4]) : 0;
        if (repetitions < 1 || warmup < 0) throw std::runtime_error("repeticoes/aquecimento invalidos");
        const Instance instance = read_instance(argv[2]);
        Result expected{};
        for (int i = 0; i < warmup + repetitions; ++i) {
            const auto start = std::chrono::steady_clock::now();
            const Result result = algorithm == "brute" ? brute_force(instance) : backtracking(instance);
            const auto end = std::chrono::steady_clock::now();
            if (i == 0) expected = result;
            else if (result != expected) throw std::runtime_error("resultados divergentes entre repeticoes");
            if (i >= warmup) {
                const auto ns = std::chrono::duration_cast<std::chrono::nanoseconds>(end - start).count();
                std::cout << result.first << ',' << result.second << ',' << ns << '\n';
            }
        }
        return 0;
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
