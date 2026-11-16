// Perfila as alocacoes dinamicas das MESMAS funcoes do executavel cronometrado.
// O contador intercepta operator new apenas enquanto o algoritmo e executado.
#include <algorithm>
#include <cstddef>
#include <cstdlib>
#include <iostream>
#include <new>

namespace {
struct alignas(std::max_align_t) AllocationHeader {
    std::size_t size;
    bool tracked;
};

bool tracking = false;
std::size_t live_bytes = 0;
std::size_t peak_bytes = 0;
}

void* operator new(std::size_t size) {
    if (size > static_cast<std::size_t>(-1) - sizeof(AllocationHeader)) throw std::bad_alloc();
    void* raw = std::malloc(sizeof(AllocationHeader) + std::max<std::size_t>(size, 1));
    if (!raw) throw std::bad_alloc();
    auto* header = static_cast<AllocationHeader*>(raw);
    header->size = size;
    header->tracked = tracking;
    if (tracking) {
        live_bytes += size;
        peak_bytes = std::max(peak_bytes, live_bytes);
    }
    return header + 1;
}

#if defined(__GNUC__)
__attribute__((noinline))
#endif
void operator delete(void* ptr) noexcept {
    if (!ptr) return;
    auto* header = static_cast<AllocationHeader*>(ptr) - 1;
    if (header->tracked) live_bytes -= header->size;
    std::free(header);
}

void* operator new[](std::size_t size) { return ::operator new(size); }
void operator delete[](void* ptr) noexcept { ::operator delete(ptr); }
void operator delete(void* ptr, std::size_t) noexcept { ::operator delete(ptr); }
void operator delete[](void* ptr, std::size_t) noexcept { ::operator delete(ptr); }

// Reutiliza read_instance, brute_force e backtracking sem alterar o binario
// de tempo nem duplicar as implementacoes. Apenas o main e renomeado.
#define main nqueens_timing_main
#include "nqueens.cpp"
#undef main

int main(int argc, char** argv) {
    try {
        if (argc != 3) throw std::runtime_error("uso: memory_profile <brute|backtracking> <entrada>");
        const std::string algorithm = argv[1];
        if (algorithm != "brute" && algorithm != "backtracking") throw std::runtime_error("algoritmo invalido");
        const Instance instance = read_instance(argv[2]);
        live_bytes = peak_bytes = 0;
        tracking = true;
        const Result result = algorithm == "brute" ? brute_force(instance) : backtracking(instance);
        tracking = false;
        if (live_bytes != 0) throw std::runtime_error("alocacoes nao liberadas ao final do algoritmo");
        std::cout << result.first << ',' << result.second << ',' << peak_bytes << '\n';
        return 0;
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
