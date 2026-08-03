"""Tests del UnitOfWork i dels use cases d'aplicació.

Verifiquen que el UoW coordina repositoris i transaccions, i que els
serveis d'aplicació orquestren repos+domini+UoW.
"""

from __future__ import annotations

import pytest

from app.application import UnitOfWork, transaction
from app.application.services import GetPersonUseCase, MergePersonsUseCase
from app.domain.exceptions import ConflictError, EntityNotFoundError
from app.models import Person


def test_unit_of_work_instantiates_repos(test_session):
    uow = UnitOfWork(test_session)
    assert uow.persons is not None
    assert uow.families is not None
    assert uow.places is not None
    uow.rollback()


def test_uow_commit_persists(test_session):
    uow = UnitOfWork(test_session)
    uow.persons.add(Person(xref="I1", given_name="Joan", surname="Miró"))
    uow.commit()

    uow2 = UnitOfWork(test_session)
    assert uow2.persons.get_by_xref("I1") is not None


def test_uow_rollback_aborts(test_session):
    uow = UnitOfWork(test_session)
    uow.persons.add(Person(xref="I2", given_name="Anna", surname="Puig"))
    uow.rollback()
    # rollback completa la sessió; es crea una nova per consultar.
    check = UnitOfWork(test_session)
    assert check.persons.get_by_xref("I2") is None


def test_transaction_context_manager_closes_but_does_not_commit(test_session):
    # El context manager del UoW tanca la sessió; NOMÉS `transaction()` fa
    # commit. Això fa explícita l'elecció de quan fer commit.
    with UnitOfWork(test_session) as uow:
        uow.persons.add(Person(xref="I3", given_name="Pau", surname="Dalmau"))
    fresh = UnitOfWork(test_session)
    assert fresh.persons.get_by_xref("I3") is None


def test_transaction_helper_commits(test_session):
    uow = UnitOfWork(test_session)
    with transaction(uow):
        uow.persons.add(Person(xref="I4", given_name="Lluis", surname="Coma"))
    fresh = UnitOfWork(test_session)
    assert fresh.persons.get_by_xref("I4") is not None


class TestGetPersonUseCase:
    def test_returns_domain_entity(self, test_session):
        uow = UnitOfWork(test_session)
        uow.persons.add(Person(xref="I10", given_name="Núria", surname="Nora"))
        uow.commit()

        person_id = uow.persons.get_by_xref("I10").id
        case = GetPersonUseCase(UnitOfWork(test_session))
        found = case.execute(person_id)
        assert found.surname == "Nora"

    def test_not_found_raises(self, test_session):
        case = GetPersonUseCase(UnitOfWork(test_session))
        with pytest.raises(EntityNotFoundError):
            case.execute(999_999)


class TestMergePersonsUseCase:
    def test_merge_same_id_raises(self, test_session):
        case = MergePersonsUseCase(UnitOfWork(test_session))
        with pytest.raises(ConflictError):
            case.merge(1, 1)

    def test_merge_missing_raises(self, test_session):
        case = MergePersonsUseCase(UnitOfWork(test_session))
        with pytest.raises(ConflictError):
            case.merge(1, 999_999)
